from app.ai.chains.workout_chain import generate_program

def generate_plan(profile, user_id=None):
    return generate_program(profile, user_id=user_id)