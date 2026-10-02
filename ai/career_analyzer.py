from assessment_analyzer import start_assessment, find_skill_gaps
from roadmap_generator import generate_roadmap
from career_analyzer_data import CAREER_SKILLS, get_career_skills
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
