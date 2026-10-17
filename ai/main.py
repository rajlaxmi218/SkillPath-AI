from fastapi import FastAPI
from pydantic import BaseModel
from google import genai
import os
import json
from dotenv import load_dotenv
from career_analyzer_data import CAREER_SKILLS, get_career_skills
from assessment_analyzer import CAREER_ASSESSMENTS, find_skill_gaps
from roadmap_generator import generate_roadmap
import uuid
from question_generator import generate_career_questions

app = FastAPI()

load_dotenv()
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
ASSESSMENT_SESSIONS = {}


def fallback_questions(career):
    questions = []
    for skill, data in CAREER_ASSESSMENTS.get(career, {}).items():
        questions.append({
            "skill": skill,
            "difficulty": "easy",
            "question": data["question"],
            "options": data["options"],
            "answer": data["answer"]
        })
    return questions


class AssessmentSubmission(BaseModel):
    career: str
    answers: dict


class ChatMessage(BaseModel):
    message: str


class InterviewAnswer(BaseModel):
    career: str
    question: str
    answer: str    

class ReadinessRequest(BaseModel):
    career: str
    skill_results: dict
    interview_feedback: str = ""    

class AssessmentStartRequest(BaseModel):
    career: str


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


@app.post("/assessment")
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
        model="gemini-3.5-flash-lite",
        contents=chat.message
    )
    return {"reply": response.text}


@app.get("/lesson/{topic}")
def generate_lesson(topic: str):
    prompt = f"""
You are a patient, clear teacher creating a short lesson for a beginner student.

Topic: {topic}

Write a concise lesson that includes:
1. A simple explanation of the concept (2-3 sentences)
2. One small, clear code example or real-world example (if applicable)
3. 2-3 key points to remember

Keep it beginner-friendly and encouraging. Do not make it too long.
"""

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            response = gemini_client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )
            return {"topic": topic, "lesson": response.text}
        except Exception as e:
            if attempt == max_attempts:
                return {"topic": topic, "lesson": "Lesson unavailable right now. Please try again later.", "error": str(e)}


@app.get("/quiz/{topic}")
def generate_quiz(topic: str):
    prompt = f"""
Create one multiple-choice question to test a beginner's knowledge of: {topic}

Respond ONLY with valid JSON in exactly this format, and nothing else (no markdown, no explanation):
{{
  "question": "...",
  "options": ["...", "...", "...", "..."],
  "answer": "..."
}}

The "answer" must be exactly one of the strings in "options".
"""

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            response = gemini_client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )
            cleaned_text = response.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            quiz_data = json.loads(cleaned_text)
            return {"topic": topic, "quiz": quiz_data}
        except Exception as e:
            if attempt == max_attempts:
                return {"topic": topic, "quiz": None, "error": str(e)}

@app.get("/interview-question/{career}")
def get_interview_question(career: str):
    prompt = f"""
You are a technical interviewer conducting a mock interview for a {career} position.

Ask ONE realistic, common interview question suitable for a beginner-to-intermediate candidate in this field.
It can be conceptual or practical.

Respond with ONLY the question text, nothing else — no numbering, no extra commentary.
"""

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            response = gemini_client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )
            return {"career": career, "question": response.text.strip()}
        except Exception as e:
            if attempt == max_attempts:
                return {"career": career, "question": None, "error": str(e)}


@app.post("/interview-feedback")
def get_interview_feedback(submission: InterviewAnswer):
    prompt = f"""
You are a supportive technical interviewer reviewing a candidate's answer for a {submission.career} position.

Interview Question: {submission.question}
Candidate's Answer: {submission.answer}

Give brief, constructive feedback that includes:
1. What was good about the answer
2. What could be improved or added
3. A rating out of 5 for this answer

Keep it encouraging and specific. Keep the response short (4-6 sentences total).
"""

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            response = gemini_client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )
            return {"feedback": response.text.strip()}
        except Exception as e:
            if attempt == max_attempts:
                return {"feedback": "Feedback unavailable right now. Please try again later.", "error": str(e)}

@app.post("/readiness-report")
def generate_readiness_report(submission: ReadinessRequest):
    known_skills = [skill for skill, status in submission.skill_results.items() if status == "Known"]
    gap_skills = [skill for skill, status in submission.skill_results.items() if status == "Needs Improvement"]

    prompt = f"""
You are a career mentor writing a final readiness report for a student pursuing: {submission.career}

Skills they already know: {', '.join(known_skills) if known_skills else 'None yet'}
Skills they still need to improve: {', '.join(gap_skills) if gap_skills else 'None - fully ready!'}

Mock interview feedback they received: {submission.interview_feedback if submission.interview_feedback else 'No mock interview completed yet.'}

Write a short, honest readiness report that includes:
1. An overall readiness level (Not Ready / Getting There / Almost Ready / Job Ready)
2. A brief summary of their strengths
3. The key areas they should focus on before applying for jobs
4. One encouraging closing sentence

Keep it concise, honest, and motivating. Around 150 words.
"""

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            response = gemini_client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )
            return {"career": submission.career, "readiness_report": response.text.strip()}
        except Exception as e:
            if attempt == max_attempts:
                return {"career": submission.career, "readiness_report": "Report unavailable right now. Please try again later.", "error": str(e)}       

@app.post("/assessment/start")
def start_assessment_session(request: AssessmentStartRequest):
    skills = get_career_skills(request.career)
    if not skills:
        return {"error": f"'{request.career}' is not a valid career"}

    questions = generate_career_questions(request.career, skills)
    source = "ai"

    if not questions:
        questions = fallback_questions(request.career)
        source = "fallback"

    session_id = str(uuid.uuid4())
    ASSESSMENT_SESSIONS[session_id] = {
        "career": request.career,
        "questions": questions
    }

    public_questions = []
    for index, q in enumerate(questions):
        public_questions.append({
            "id": index,
            "skill": q["skill"],
            "question": q["question"],
            "options": q["options"]
        })

    return {
        "session_id": session_id,
        "career": request.career,
        "source": source,
        "total_questions": len(public_questions),
        "questions": public_questions
    }                 