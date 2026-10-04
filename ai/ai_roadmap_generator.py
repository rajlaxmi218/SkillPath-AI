import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


def generate_ai_roadmap(career, skill_results):
    known_skills = [skill for skill, status in skill_results.items() if status == "Known"]
    gap_skills = [skill for skill, status in skill_results.items() if status == "Needs Improvement"]

    prompt = f"""
You are a career mentor creating a short, personalized learning roadmap.

Career: {career}
Skills the student already knows: {', '.join(known_skills) if known_skills else 'None'}
Skills the student needs to learn: {', '.join(gap_skills) if gap_skills else 'None'}

Create a week-by-week learning roadmap that:
- Skips or briefly mentions skills already known
- Focuses learning weeks on the skills that need improvement
- Is concise, practical, and encouraging
- Uses a simple "Week 1: ...", "Week 2: ..." format
"""

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < max_attempts:
                print("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                return "AI roadmap unavailable right now. Please try again later."


if __name__ == "__main__":
    test_results = {
        "HTML": "Known",
        "CSS": "Known",
        "JavaScript": "Needs Improvement",
        "React": "Needs Improvement"
    }
    roadmap_text = generate_ai_roadmap("Web Development", test_results)
    print(roadmap_text)