import os
import json
from datetime import datetime
import PyPDF2
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson.objectid import ObjectId
import re

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

# --- MongoDB Configuration ---
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "main_db"

mongo_client = None
mongo_profile_collection = None
mongo_chat_collection = None
mongo_resume_upload_collection = None
mongo_resume_parsed_collection = None

try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    mongo_client.admin.command('ismaster')
    mongo_db = mongo_client[DB_NAME]
    mongo_profile_collection = mongo_db["profile_resume"]
    mongo_chat_collection = mongo_db["ai_chat"]
    mongo_resume_upload_collection = mongo_db["resume_upload"]
    mongo_resume_parsed_collection = mongo_db["resume_parsed"]
    print("MongoDB connection successful.")
except ConnectionFailure as e:
    print(f"ERROR: MongoDB Connection Failed. {e}")
except Exception as e:
    print(f"MongoDB Error: {e}")

# Gemini Config
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    model = None

# --- CONFIG ---
RESUME_STEPS = [
    {"field": "full_name",
     "question": "Let's build your profile. **Upload your Resume (PDF)** or tell me your **Full Name**.",
     "mandatory": True, "type": "text", "suggestions": []},
    {"field": "email", "question": "What is your **Email Address**?", "mandatory": True, "type": "email",
     "suggestions": []},
    {"field": "phone", "question": "What is your **Phone Number**?", "mandatory": True, "type": "phone",
     "suggestions": []},
    {"field": "experience_level", "question": "What is your **Experience Level**?", "mandatory": True,
     "type": "selection", "suggestions": ["Intern", "Entry Level", "Mid Level", "Senior", "Lead"]},
    {"field": "domain", "question": "Which **Industry or Domain** are you interested in?", "mandatory": True,
     "type": "text", "suggestions": ["Software Development", "Data Science", "Finance", "Marketing"]},
    {"field": "job_title", "question": "Target **Job Title**?", "mandatory": True, "type": "text", "suggestions": []},
    {"field": "skills", "question": "Top 3-5 **Skills**? (Type 'Suggest Skills' for AI help)", "mandatory": True,
     "type": "text", "suggestions": []},
    {"field": "summary", "question": "Professional **Summary**? (Type 'Generate' to see options)", "mandatory": True,
     "type": "long_text", "suggestions": ["Generate Options", "Show Example"]},
    {"field": "critique", "question": "Profile complete! Review your profile. Check ATS Score or Submit.",
     "mandatory": False, "type": "final", "suggestions": ["Check ATS Score", "Submit"]}
]


def find_next_step(current_data):
    for i, step in enumerate(RESUME_STEPS):
        field = step['field']
        if step['mandatory'] and not current_data.get(field):
            return i
        if step['field'] == 'critique':
            if all(current_data.get(s['field']) for s in RESUME_STEPS if s['mandatory']):
                return i
    return -1


def log_resume_interaction(session_id, user_text, ai_text, step_index, collected_data):
    if mongo_client is None: return
    if not ObjectId.is_valid(session_id): return
    oid = ObjectId(session_id)

    interaction = {
        'timestamp': datetime.utcnow(),
        'step': step_index,
        'user_said': user_text,
        'ai_replied': ai_text,
        'snapshot': collected_data
    }
    mongo_chat_collection.update_one(
        {'_id': oid},
        {
            '$push': {'interactions': interaction},
            '$setOnInsert': {'created_at': datetime.utcnow()}
        },
        upsert=True
    )


def get_dynamic_suggestions(field, data):
    try:
        if field == "job_title":
            prompt = f"List 3 standard job titles for a '{data.get('experience_level')}' professional in '{data.get('domain')}'. Output comma-separated."
            response = model.generate_content(prompt)
            return [s.strip() for s in response.text.split(',') if s.strip()][:3]
        if field == "skills":
            prompt = f"List 6 distinct single skills for a '{data.get('job_title')}'. Output comma-separated."
            response = model.generate_content(prompt)
            return [s.strip() for s in response.text.split(',') if s.strip()][:6]
    except:
        return []
    return []


# --- ROUTES ---
@app.route('/')
def home(): return render_template('index.html')


@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    if 'file' not in request.files: return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({'error': 'No file selected'}), 400

    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"

        resume_id = ObjectId()
        if mongo_resume_upload_collection is not None:
            mongo_resume_upload_collection.insert_one({
                "_id": resume_id, "resume_id": resume_id, "filename": file.filename,
                "raw_text_content": text, "timestamp": datetime.utcnow()
            })

        prompt = f"""Extract details to JSON. Keys: full_name, email, phone, experience_level, domain, job_title, skills, summary. Text: {text[:4000]}"""
        response = model.generate_content(prompt)
        cleaned_text = response.text.replace('```json', '').replace('```', '').strip()
        extracted_data = json.loads(cleaned_text)

        if mongo_resume_parsed_collection is not None:
            mongo_resume_parsed_collection.insert_one({
                "resume_id": resume_id, "parsed_data": extracted_data, "timestamp": datetime.utcnow()
            })

        return jsonify({'success': True, 'data': extracted_data, 'resume_id': str(resume_id), 'message': "Analyzed."})
    except Exception as e:
        return jsonify({'error': 'Failed to process PDF'}), 500


@app.route('/api/resume-chat', methods=['POST'])
def resume_chat():
    data = request.json
    user_input = data.get('message', '').strip()
    collected_data = data.get('data', {})
    current_step_index = data.get('step', -1)
    session_id = data.get('session_id') or str(ObjectId())

    # Special Commands
    if user_input.lower() == 'check ats score':
        prompt = f"ATS Scan. Profile: {collected_data}. Score (0-100), 3 missing keywords, feedback."
        try:
            ai_resp = model.generate_content(prompt)
            ai_text = f"**ATS Analysis:**\n\n{ai_resp.text}"

            next_step_idx = find_next_step(collected_data)
            if next_step_idx != -1:
                next_rule = RESUME_STEPS[next_step_idx]
                ai_text += f"\n\n---\n**Resuming:** {next_rule['question']}"
                sugs = next_rule['suggestions']
                if next_rule['field'] in ['job_title', 'skills']:
                    dyn = get_dynamic_suggestions(next_rule['field'], collected_data)
                    if dyn: sugs = dyn
                log_resume_interaction(session_id, user_input, ai_text, next_step_idx, collected_data)
                return jsonify(
                    {'response': ai_text, 'keep_step': True, 'question': next_rule['question'], 'suggestions': sugs,
                     'session_id': session_id, 'next_step': next_step_idx})
            else:
                log_resume_interaction(session_id, user_input, ai_text, current_step_index, collected_data)
                return jsonify({'response': ai_text, 'keep_step': True, 'question': RESUME_STEPS[-1]['question'],
                                'suggestions': RESUME_STEPS[-1]['suggestions'], 'session_id': session_id})
        except:
            return jsonify({'error': "ATS failed.", 'keep_step': True, 'session_id': session_id})

    if user_input.lower() == 'submit':
        ai_text = "Interview complete! Please click the green 'Submit Profile' button."
        log_resume_interaction(session_id, user_input, ai_text, current_step_index, collected_data)
        return jsonify({'response': ai_text, 'finished': True, 'data': collected_data, 'session_id': session_id})

    # Validation
    just_saved_summary = False
    if current_step_index != -1 and user_input:
        current_rule = RESUME_STEPS[current_step_index]
        error_msg = None
        if current_rule['field'] == 'full_name' and any(char.isdigit() for char in user_input):
            error_msg = "Name cannot contain numbers."
        elif current_rule['type'] == 'email' and not re.match(r"[^@]+@[^@]+\.[^@]+", user_input):
            error_msg = "Invalid email format."
        elif current_rule['type'] == 'phone' and not re.search(r"\d{10}", user_input):
            error_msg = "Invalid phone."

        if error_msg:
            log_resume_interaction(session_id, user_input, error_msg, current_step_index, collected_data)
            return jsonify({'error': error_msg, 'keep_step': True, 'session_id': session_id})

        if current_rule['field'] == 'summary' and 'generate' in user_input.lower():
            try:
                prompt = f"Write 2 summaries for {collected_data.get('job_title')}, skills {collected_data.get('skills')}. Separate by '|||'. No headers."
                ai_resp = model.generate_content(prompt)
                raw_text = ai_resp.text
                options = [opt.strip() for opt in raw_text.split('|||') if opt.strip()]
                ai_text = "Here are two summary options. Click one to auto-fill."
                log_resume_interaction(session_id, user_input, ai_text + f" {options}", current_step_index,
                                       collected_data)
                return jsonify(
                    {'response': ai_text, 'suggestions': options, 'keep_step': True, 'session_id': session_id})
            except:
                return jsonify({'error': "Generation failed.", 'keep_step': True, 'session_id': session_id})

        collected_data[current_rule['field']] = user_input
        if current_rule['field'] == 'summary': just_saved_summary = True

    # Next Step
    next_step_index = find_next_step(collected_data)

    if next_step_index == -1:
        ai_text = "Profile complete! Please review and submit."
        if just_saved_summary: ai_text = "Summary updated.\n\n" + ai_text
        log_resume_interaction(session_id, user_input, ai_text, current_step_index, collected_data)
        return jsonify({'response': ai_text, 'finished': True, 'data': collected_data, 'session_id': session_id})

    next_rule = RESUME_STEPS[next_step_index]
    ai_text = next_rule['question']
    if just_saved_summary: ai_text = "Summary updated.\n\n" + ai_text

    dynamic_suggestions = next_rule['suggestions']
    if next_rule['field'] in ['job_title', 'skills']:
        generated = get_dynamic_suggestions(next_rule['field'], collected_data)
        if generated: dynamic_suggestions = generated

    ui_response_text = ""
    if current_step_index == -1 and not user_input:
        if collected_data.get('full_name'):
            ai_text = f"Welcome back, **{collected_data['full_name']}**! Resuming... " + ai_text
        else:
            ai_text = "Hello! Let's build your resume. " + ai_text
        ui_response_text = ai_text

    log_resume_interaction(session_id, user_input, ai_text, next_step_index, collected_data)

    return jsonify({'response': ui_response_text, 'next_step': next_step_index, 'question': next_rule['question'],
                    'suggestions': dynamic_suggestions, 'data': collected_data, 'session_id': session_id})


@app.route('/api/submit-resume', methods=['POST'])
def submit_resume():
    if mongo_client is None: return jsonify({'error': 'DB Error'}), 500
    try:
        new_profile = request.json
        session_id_str = new_profile.pop('resume_session_id', None)
        upload_id_str = new_profile.pop('upload_resume_id', None)

        new_profile['chat_session_id'] = ObjectId(session_id_str) if session_id_str and ObjectId.is_valid(
            session_id_str) else None
        new_profile['resume_upload_id'] = ObjectId(upload_id_str) if upload_id_str and ObjectId.is_valid(
            upload_id_str) else None
        new_profile['submitted_at'] = datetime.utcnow()

        mongo_profile_collection.insert_one(new_profile)
        return jsonify({'status': 'success', 'message': 'Profile saved to MongoDB'})
    except Exception as e:
        print(e)
        return jsonify({'error': 'Error saving'}), 500


if __name__ == '__main__':
    app.run(port=5001, debug=True)  # Runs on Port 5001 to avoid conflict