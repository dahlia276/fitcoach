from app.ai.chains.workout_chain import generate


def generate_plan(user):
    return generate(user)