from fastapi import FastAPI
from career_analyzer_data import CAREER_SKILLS

app = FastAPI()


@app.get("/")
def home():
    return {"message": "SkillPath AI backend is running"}


@app.get("/careers")
def get_careers():
    return {"careers": list(CAREER_SKILLS.keys())}