import re
import random
from llm import generate_json, LLMError
from assessment_analyzer import CAREER_ASSESSMENTS

DIFFICULTIES = ("easy", "medium", "hard")
QUESTION_TYPES = ("conceptual", "code_output", "debugging", "scenario")
MIN_QUESTIONS = 8        # fewer than this is not accepted as an assessment
EXTRA_CANDIDATES = 4     # ask for extra, because some will be rejected


def normalise_text(text):
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def is_valid_question(q, skills):
    if not isinstance(q, dict):
        return False
    text = q.get("question")
    options = q.get("options")
    if not isinstance(text, str) or not text.strip():
        return False
    if not isinstance(options, list) or len(options) != 4:
        return False
    if not all(isinstance(o, str) and o.strip() for o in options):
        return False
    if len({o.strip().lower() for o in options}) != 4:
        return False
    return (
        q.get("answer") in options
        and q.get("skill") in skills
        and q.get("difficulty") in DIFFICULTIES
        and q.get("question_type") in QUESTION_TYPES
        and isinstance(q.get("explanation"), str)
    )


def filter_valid(raw, skills):
    valid, seen = [], set()
    if not isinstance(raw, list):
        return valid

    for q in raw:
        if isinstance(q, dict) and q.get("question_type") not in QUESTION_TYPES:
            q["question_type"] = "conceptual"
        if not is_valid_question(q, skills):
            continue
        key = normalise_text(q["question"])
        if key in seen:
            continue
        seen.add(key)
        valid.append({
            "skill": q["skill"],
            "difficulty": q["difficulty"],
            "question_type": q["question_type"],
            "question": q["question"].strip(),
            "options": list(q["options"]),
            "answer": q["answer"],
            "explanation": q["explanation"].strip(),
        })
    return valid


def verify_answers(questions):
    """Ask Gemini to answer WITHOUT seeing the key. Drop questions where it disagrees.
    Returns (questions, was_verified)."""
    items = [
        {"n": i, "question": q["question"], "options": q["options"]}
        for i, q in enumerate(questions)
    ]
    prompt = f"""
You are an expert examiner. For each question, choose the single best option.

Questions:
{items}

Respond ONLY with a valid JSON array, no markdown, in exactly this format:
[{{"n": 0, "choice": "<exact text of the chosen option>"}}]
"""
    try:
        replies = generate_json(prompt)
    except LLMError as e:
        print(f"[verify] skipped: {e}")
        return questions, False

    if not isinstance(replies, list):
        return questions, False

    choices = {r.get("n"): r.get("choice") for r in replies if isinstance(r, dict)}
    if not choices:
        return questions, False

    verified = [q for i, q in enumerate(questions) if choices.get(i) == q["answer"]]
    print(f"[verify] kept {len(verified)} of {len(questions)} questions")
    return verified, True


def select_questions(valid, skills, count):
    chosen = []
    for skill in skills:  # one easy question per skill first
        for q in valid:
            if q["skill"] == skill and q["difficulty"] == "easy":
                chosen.append(q)
                break
    for q in valid:
        if len(chosen) >= count:
            break
        if q not in chosen:
            chosen.append(q)
    return chosen[:count]


def covers_all_skills(questions, skills):
    return {q["skill"] for q in questions} == set(skills)


def finalise(questions):
    for q in questions:
        random.shuffle(q["options"])  # answer is stored as text, so it stays correct
    return questions


def get_fallback_questions(career):
    """Your hand-written questions: 1 per skill, so fewer than 10."""
    questions = []
    for skill, data in CAREER_ASSESSMENTS.get(career, {}).items():
        questions.append({
            "skill": skill,
            "difficulty": "easy",
            "question_type": "conceptual",
            "question": data["question"],
            "options": list(data["options"]),
            "answer": data["answer"],
            "explanation": "",
        })
    return finalise(questions)


def generate_career_questions(career, skills, count=10, verify=True):
    skills_text = ", ".join(skills)

    prompt = f"""
Create {count + EXTRA_CANDIDATES} multiple-choice questions to assess a student's knowledge for the {career} career path.

The skills for this career are: {skills_text}

Rules:
- Give EVERY skill exactly one "easy" question (basic level, answerable by a beginner who studied the topic)
- Use the remaining questions as "medium" or "hard" questions for the more important skills
- "skill" must be exactly one of the skills from the list
- "difficulty" must be "easy", "medium" or "hard"
- "question_type" must be "conceptual", "code_output", "debugging" or "scenario"
- For programming skills, include some "code_output" or "debugging" questions with a short code snippet inside the question text
- Each question has exactly 4 different options
- "answer" must be exactly one of the strings in "options"
- "explanation" is 1-2 sentences explaining why the answer is correct
- Questions must be technically correct and unambiguous. Do not repeat questions.

Respond ONLY with a valid JSON array, no markdown, no extra text, in exactly this format:
[
  {{"skill": "...", "difficulty": "easy", "question_type": "conceptual", "question": "...", "options": ["...", "...", "...", "..."], "answer": "...", "explanation": "..."}}
]
"""

    best = []
    for attempt in range(1, 3):
        try:
            raw = generate_json(prompt)
        except LLMError as e:
            print(f"[generator] Gemini failed: {e}")
            break

        valid = filter_valid(raw, skills)
        if verify and valid:
            valid, _ = verify_answers(valid)

        selected = select_questions(valid, skills, count)
        if len(selected) == count and covers_all_skills(selected, skills):
            return finalise(selected)

        if len(selected) > len(best):
            best = selected
        print(f"[generator] attempt {attempt}: {len(selected)} usable questions, retrying...")

    return finalise(best) if len(best) >= MIN_QUESTIONS else []


if __name__ == "__main__":
    from career_analyzer_data import get_career_skills

    career = "Web Development"
    questions = generate_career_questions(career, get_career_skills(career))
    print(f"\nGot {len(questions)} questions\n")

    for i, q in enumerate(questions, start=1):
        print(f"{i}. [{q['skill']} | {q['difficulty']} | {q['question_type']}] {q['question']}")
        for option in q["options"]:
            print("   -", option)
        print("   Answer:", q["answer"])
        print("   Why:", q["explanation"])
        print()