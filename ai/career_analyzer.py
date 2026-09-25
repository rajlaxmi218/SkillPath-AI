from assessment_analyzer import start_assessment, find_skill_gaps
from roadmap_generator import generate_roadmap
CAREER_SKILLS = {
    "DSA & Programming": [
        "Programming Fundamentals",
        "OOP",
        "Data Structures",
        "Algorithms",
        "Problem Solving",
        "Competitive Programming"
    ],

    "Web Development": [
        "HTML",
        "CSS",
        "JavaScript",
        "Git & GitHub",
        "React",
        "Backend",
        "Database",
        "Full Stack Projects"
    ],

    "Data Analytics": [
        "Excel",
        "SQL",
        "Python",
        "Statistics",
        "Pandas",
        "Data Visualization",
        "Power BI / Tableau",
        "Projects"
    ],

    "AI & Prompt Engineering": [
        "Python Basics",
        "AI Fundamentals",
        "Generative AI",
        "Prompt Engineering",
        "APIs",
        "LLM Concepts",
        "AI Applications",
        "Projects"
    ],

    "Machine Learning": [
        "Python",
        "Mathematics",
        "Statistics",
        "NumPy",
        "Pandas",
        "Machine Learning",
        "Model Evaluation",
        "Projects"
    ],

    "Cloud Computing": [
        "Networking Basics",
        "Linux",
        "Cloud Fundamentals",
        "AWS / Azure / GCP",
        "Cloud Storage",
        "Compute",
        "Deployment",
        "Cloud Projects"
    ],

    "App Development": [
        "Programming Basics",
        "UI Fundamentals",
        "Android / Flutter",
        "APIs",
        "Database",
        "Authentication",
        "App Deployment",
        "Projects"
    ],

    "Cybersecurity": [
        "Networking",
        "Linux",
        "Cybersecurity Fundamentals",
        "Cryptography",
        "Web Security",
        "Ethical Security Concepts",
        "Security Tools",
        "Projects"
    ],

    "UI/UX Design": [
        "Design Fundamentals",
        "User Research",
        "Wireframing",
        "Figma",
        "Prototyping",
        "Usability",
        "Design Systems",
        "Portfolio Projects"
    ]
}
def get_career_skills(career):
    return CAREER_SKILLS.get(career, [])
print("Choose your career path:\n")

career_list = list(CAREER_SKILLS.keys())

for index, career in enumerate(career_list, start=1):
    print(f"{index}. {career}")

career_choice = input("\nEnter the number of your career path: ").strip()

if career_choice.isdigit() and 1 <= int(career_choice) <= len(career_list):
    selected_career = career_list[int(career_choice) - 1]
else:
    print("\nInvalid choice. Defaulting to Web Development.")
    selected_career = "Web Development"

skills = get_career_skills(selected_career)
print("Selected Career:", selected_career)
print("Required Skills:")

for skill in skills:
    print("-", skill)

print("\nChoose your learning mode:")
print("1. Complete Beginner")
print("2. Take Assessment")

choice = input("Enter your choice (1 or 2): ")

if choice == "1":
    print("\nYou are a Complete Beginner.")
    print("Starting your roadmap from the basics.")

    beginner_results = {skill: "Needs Improvement" for skill in skills}
    generate_roadmap(selected_career, beginner_results)
elif choice == "2":
    print("\nAssessment selected.")
    print("We will analyze your current skill level.\n")

    results = start_assessment(selected_career, skills)
    skill_gaps = find_skill_gaps(results)

    print("\nSkill Gaps:")
    for skill in skill_gaps:
        print("-", skill)
    generate_roadmap(selected_career, results)

else:
    print("\nInvalid choice. Please select 1 or 2.")
