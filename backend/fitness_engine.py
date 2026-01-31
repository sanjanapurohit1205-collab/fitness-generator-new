import random

# Data Pools
EXERCISE_POOLS = {
    "warmup": ["Jumping Jacks", "High Knees", "Arm Circles", "Torso Twists", "Light Jog"],
    "push": ["Push-ups", "Incline Push-ups", "Diamond Push-ups", "Pike Push-ups", "Dips (Chair)", "Wide Push-ups"],
    "pull": ["Pull-ups", "Chin-ups", "Inverted Rows", "Superman", "Doorframe Rows", "Back Extensions"],
    "legs": ["Squats", "Lunges", "Glute Bridges", "Calf Raises", "Bulgarian Split Squats", "Wall Sit"],
    "core": ["Plank", "Crunches", "Leg Raises", "Russian Twists", "Bicycle Crunches", "Mountain Climbers"],
    "cardio": ["Burpees", "Jump Rope", "Sprint Intervals", "Box Jumps", "Shadow Boxing", "Stair Climbing"]
}

def calculate_bmi(height_cm, weight_kg):
    try:
        h_m = float(height_cm) / 100
        w_kg = float(weight_kg)
        return round(w_kg / (h_m ** 2), 1)
    except:
        return 0

def _get_exercises(category, count=3):
    pool = EXERCISE_POOLS.get(category, [])
    return random.sample(pool, min(len(pool), count))

def generate_workout(user_data):
    goal = user_data.get('goal', '').lower()
    
    # Random selection ensures "different plans every time"
    warmup = [f"{e} 30s" for e in _get_exercises("warmup", 2)]
    
    plan = []
    
    if 'fat' in goal or 'loss' in goal or 'weight' in goal:
        focus = "Fat Loss & Cardio"
        # Day 1: Full Body HIIT
        d1_ex = _get_exercises("cardio", 2) + _get_exercises("legs", 1) + _get_exercises("push", 1)
        plan.append({"day": "Day 1 - HIIT & Burn", "exercises": warmup + [f"{e} 3x15" for e in d1_ex]})
        
        # Day 2: Active
        plan.append({"day": "Day 2 - Cardio", "exercises": ["Jogging/Running 20m", "Stretching 10m"]})
        
        # Day 3: Core & Tone
        d3_ex = _get_exercises("core", 3) + _get_exercises("pull", 1)
        plan.append({"day": "Day 3 - Core Blaster", "exercises": warmup + [f"{e} 3x12" for e in d3_ex]})
        
    elif 'muscle' in goal or 'gain' in goal or 'build' in goal:
        focus = "Muscle Building"
        # Day 1: Push
        d1_ex = _get_exercises("push", 3) + _get_exercises("core", 1)
        plan.append({"day": "Day 1 - Push Strength", "exercises": warmup + [f"{e} 3x8-12" for e in d1_ex]})
        
        # Day 2: Pull
        d2_ex = _get_exercises("pull", 3) + _get_exercises("legs", 1)
        plan.append({"day": "Day 2 - Pull & Back", "exercises": warmup + [f"{e} 3x8-12" for e in d2_ex]})
        
        # Day 3: Legs
        d3_ex = _get_exercises("legs", 3) + _get_exercises("core", 1)
        plan.append({"day": "Day 3 - Leg Day", "exercises": warmup + [f"{e} 4x10" for e in d3_ex]})
        
    else: # General
        focus = "General Fitness"
        # Day 1: Upper
        d1_ex = _get_exercises("push", 2) + _get_exercises("pull", 2)
        plan.append({"day": "Day 1 - Upper Body", "exercises": warmup + [f"{e} 3x10" for e in d1_ex]})
        
        # Day 2: Active
        plan.append({"day": "Day 2 - Mobility", "exercises": ["Yoga 20m", "Walk 15m"]})
        
        # Day 3: Lower & Core
        d3_ex = _get_exercises("legs", 2) + _get_exercises("core", 2)
        plan.append({"day": "Day 3 - Lower & Core", "exercises": warmup + [f"{e} 3x12" for e in d3_ex]})

    return plan

def generate_diet(user_data):
    diet_type = user_data.get('diet_type', 'Veg').lower()
    goal = user_data.get('goal', '').lower()
    is_gain = 'gain' in goal or 'muscle' in goal
    
    # Simple randomization for diet variety too could be added, but keeping it stable for now
    if 'veg' in diet_type and 'non' not in diet_type:
        breakfast = "Oatmeal with nuts & banana" if is_gain else "Green smoothie + soaked almonds"
        lunch = "Paneer butter masala + brown rice" if is_gain else "Dal tadka + salad + 1 roti"
        dinner = "Lentil soup + grilled veggies"
    elif 'vegan' in diet_type:
        breakfast = "Tofu Scramble with toast"
        lunch = "Chickpea Curry with Quinoa"
        dinner = "Stir-fried Tofu & Broccoli"
    else:
        breakfast = "3 Eggs Omelet + toast" if is_gain else "2 Boiled Eggs + Apple"
        lunch = "Grilled Chicken Breast + Rice" if is_gain else "Grilled Fish + Salad"
        dinner = "Chicken Soup + Steamed Veggies"

    return {"breakfast": breakfast, "lunch": lunch, "dinner": dinner}

def get_chat_response(message):
    msg = message.lower()
    
    # Smarter Rule-Based Chat
    if any(x in msg for x in ["hello", "hi", "hey"]):
        return "Hello! I'm your FitForge Coach. I can help with workouts, diet tips, or motivation. What's on your mind? 👋"
        
    if "pain" in msg or "hurt" in msg:
        return "⚠️ Safety first! If you feel sharp pain, stop immediately. Ice the area and rest. Consult a doctor if it persists."
        
    if "weight" in msg and "lose" in msg:
        return "To lose weight, focus on a calorie deficit. Move more, eat protein-rich foods, and cut down on sugar. Consistency is key! 📉"
        
    if "muscle" in msg or "gain" in msg:
        return "To build muscle, lift heavy and eat plenty of protein (1.6g per kg of bodyweight). Sleep is also crucial for recovery! 💪"
        
    if "diet" in msg or "food" in msg or "eat" in msg:
        return "Nutrition is 80% of the battle. Eat whole foods—vegetables, lean protein, and healthy fats. Stay hydrated! 🍎"
        
    if "motiv" in msg or "tired" in msg or "give up" in msg:
        quotes = [
            "Your only limit is your mind.",
            "Make yourself proud.",
            "Don't stop when you're tired. Stop when you're done."
        ]
        return f"🔥 {random.choice(quotes)} Keep pushing!"
        
    if "thank" in msg:
        return "You're welcome! Go crush that workout! 🚀"
        
    return "That's interesting! I'm best at fitness advice. Try asking about 'weight loss', 'muscle gain', 'diet tips', or 'motivation'! 🤖"