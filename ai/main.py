from fastapi import FastAPI
from pydantic import BaseModel 
from google import genai
import os
from dotenv import load_dotenv                                   # ← new import
from career_analyzer_data import CAREER_SKILLS, get_career_skills
from assessment_analyzer import CAREER_ASSESSMENTS, find_skill_gaps  # ← updated import
from roadmap_generator import generate_roadmap                    # ← new import

app = FastAPI()

load_dotenv()
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class AssessmentSubmission(BaseModel):     # ← new class goes here, after app = FastAPI()
    career: str
    answers: dict


class ChatMessage(BaseModel):
    message: str    


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


@app.get("/questions/{career}")
def get_questions(career: str):
    career_questions = CAREER_ASSESSMENTS.get(career)

    if not career_questions:
        return {"error": f"No assessment available for '{career}'"}

    questions_list = []
    for skill, data in career_questions.items():
        questions_list.append({
            "skill": skill,
            "question": data["question"],
            "options": data["options"]
        })

    return {"career": career, "questions": questions_list}


@app.post("/assessment")                  # ← new endpoint goes here, at the bottom
def submit_assessment(submission: AssessmentSubmission):
    career = submission.career
    answers = submission.answers

    career_questions = CAREER_ASSESSMENTS.get(career)
    if not career_questions:
        return {"error": f"No assessment available for '{career}'"}

    skill_results = {}

    for skill, data in career_questions.items():
        student_answer = answers.get(skill)

        if student_answer == data["answer"]:
            skill_results[skill] = "Known"
        else:
            skill_results[skill] = "Needs Improvement"

    skill_gaps = find_skill_gaps(skill_results)
    roadmap = generate_roadmap(career, skill_results)

    return {
        "career": career,
        "skill_results": skill_results,
        "skill_gaps": skill_gaps,
        "roadmap": roadmap 
    }


@app.post("/chat")
def chat_with_ai(chat: ChatMessage):
    response = gemini_client.models.generate_content(
        model="gemini-3.8-flash",
        contents=chat.message
    )
    return {"reply": response.text}