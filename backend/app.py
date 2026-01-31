from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import json
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import google.generativeai as genai
import fitness_engine # Import Local Engine

# Load environment variables
load_dotenv(override=True)

# Configure Gemini (Hybrid Setup)
api_key = os.getenv("GEMINI_API_KEY")
model = None
if api_key and not api_key.startswith("PASTE"):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("DEBUG: Gemini AI configured successfully.")
    except Exception as e:
        print(f"DEBUG: Gemini Config Failed: {e}")
else:
    print("DEBUG: No valid GEMINI_API_KEY found. Running in LOCAL Engine mode.")

app = Flask(__name__, template_folder='../frontend', static_folder='../frontend', static_url_path='/static')
app.secret_key = os.urandom(24)

# -------------------- DATABASE CONFIG --------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -------------------- MODELS --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    profile = db.relationship('FitnessProfile', backref='user', uselist=False)

class FitnessProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100))
    height = db.Column(db.String(20))
    weight = db.Column(db.String(20))
    goal = db.Column(db.String(100))
    time = db.Column(db.String(50))
    streak = db.Column(db.String(50))
    diet_type = db.Column(db.String(50))

# Create tables
with app.app_context():
    db.create_all()

# -------------------- ROUTES --------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        
        # Database Logic
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email)
            db.session.add(user)
            db.session.commit()
        
        session['user_id'] = user.id
        session['email'] = user.email
        return redirect(url_for('fitness_form'))
    
    # Check if key is configured for UI status
    key_configured = bool(os.getenv("GEMINI_API_KEY") and not os.getenv("GEMINI_API_KEY").startswith("PASTE"))
    return render_template('login.html', key_configured=key_configured)

@app.route('/settings', methods=['POST'])
def settings():
    new_key = request.form.get('api_key')
    print(f"DEBUG: settings called with key length: {len(new_key) if new_key else 0}")
    
    if new_key and new_key.strip():
        # Update .env file
        env_path = '.env'
        lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                lines = f.readlines()
        
        with open(env_path, 'w') as f:
            found = False
            for line in lines:
                if line.startswith('GEMINI_API_KEY='):
                    f.write(f'GEMINI_API_KEY={new_key.strip()}\n')
                    found = True
                elif line.strip(): # keep non-empty lines
                    f.write(line)
            if not found:
                f.write(f'\nGEMINI_API_KEY={new_key.strip()}\n')
        
        print(f"DEBUG: Written to {os.path.abspath(env_path)}")
        
        # Reload Config immediately
        os.environ["GEMINI_API_KEY"] = new_key.strip()
        try:
            genai.configure(api_key=new_key.strip())
            global model
            model = genai.GenerativeModel('gemini-1.5-flash')
            print("DEBUG: Gemini Configured Successfully via Settings")
            # flash("AI Activated Successfully!", "success")
        except Exception as e:
            print(f"DEBUG: Configuration Error: {e}")
            
    return redirect(url_for('login'))

@app.route('/form', methods=['GET', 'POST'])
def fitness_form():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get(user_id)

    if request.method == 'POST':
        profile = FitnessProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            profile = FitnessProfile(user_id=user_id)
            db.session.add(profile)
        
        profile.name = request.form.get('name')
        profile.height = request.form.get('height')
        # Ensure fallback for fields if empty
        profile.weight = request.form.get('weight') or '70'
        profile.goal = request.form.get('goal') or 'fitness'
        profile.time = request.form.get('time') or '30'
        profile.streak = request.form.get('streak')
        profile.diet_type = request.form.get('diet_type') or 'Veg'
        
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('form.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    profile = FitnessProfile.query.filter_by(user_id=user_id).first()
    
    user_data = {}
    if profile:
        user_data = {
            'name': profile.name,
            'height': profile.height,
            'weight': profile.weight,
            'goal': profile.goal,
            'time': profile.time,
            'streak': profile.streak,
            'diet_type': profile.diet_type
        }

    return render_template('dashboard.html', user_data=user_data)

# -------------------- HYBRID AI ENGINE --------------------

@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session['user_id']
    profile = FitnessProfile.query.filter_by(user_id=user_id).first()
    
    if not profile:
        return jsonify({"error": "No user data found"}), 400

    # 1. Prepare User Data
    user_data = {
        'name': profile.name,
        'height': profile.height,
        'weight': profile.weight,
        'goal': profile.goal,
        'time': profile.time,
        'diet_type': profile.diet_type
    }

    # 2. Try Gemini AI First
    if model:
        try:
            prompt = f"""
            Act as a fitness trainer. Create a 3-day workout plan and 1-day diet.
            User: {json.dumps(user_data)}
            Output STRICT JSON: {{ "workout": [{{ "day": "", "exercises": [] }}], "diet": {{ "breakfast": "", "lunch": "", "dinner": "" }} }}
            """
            response = model.generate_content(prompt)
            data = json.loads(response.text.replace('```json', '').replace('```', '').strip())
            return jsonify(data)
        except Exception as e:
            print(f"Gemini Plan Failed, swapping to Local: {e}")
    
    # 3. Fallback to Randomized Local Engine
    print("Using Local Engine for Plan.")
    try:
        workout_plan = fitness_engine.generate_workout(user_data)
        diet_plan = fitness_engine.generate_diet(user_data)
        return jsonify({
            "workout": workout_plan,
            "diet": diet_plan
        })
    except Exception as e:
        print(f"Engine Error: {e}")
        return jsonify({"error": "Engine failure"}), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    
    # 1. Try Gemini AI First
    if model:
        try:
            chat = model.start_chat()
            response = chat.send_message(f"Trainer role. User says: {message}. Keep it short.")
            return jsonify({"reply": response.text})
        except Exception as e:
             print(f"Gemini Chat Failed, swapping to Local: {e}")

    # 2. Fallback to Smarter Local Engine
    reply = fitness_engine.get_chat_response(message)
    return jsonify({"reply": reply})

# --------------------

if __name__ == "__main__":
    app.run(debug=True)
