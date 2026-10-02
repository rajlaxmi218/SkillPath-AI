from fastapi import FastAPI
from career_analyzer_data import CAREER_SKILLS, get_career_skills

app = FastAPI()


@app.get("/")
def home():
    return {"message": "SkillPath AI backend is running"}


@app.get("/careers")
def get_careers():
    return {"careers": list(CAREER_SKILLS.keys())}


@app.get("/skills/{career}")
def get_skills(career: str):
    skills = get_career_skills(career)
    if not skills:
        return {"error": f"'{career}' is not a valid career"}
    return {"career": career, "skills": skills}