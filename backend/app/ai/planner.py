from app.ai.llm import llm
from app.ai.prompts import SYSTEM_PROMPT

def generate_plan(user):

    prompt = f"""
{SYSTEM_PROMPT}

Age: {user['age']}
Weight: {user['weight']}
Goal: {user['goal']}
Experience: {user['experience']}
Equipment: {user['equipment']}
Injuries: {user['injuries']}
"""

    return llm.invoke(prompt).content