def start_assessment(skills):
    print("===== SkillPath AI Assessment =====")
    print("Answer the questions to check your current skill level.\n")

    score = 0
    skill_results = {}

    for skill in skills:
        answer = input(f"Do you know {skill}? (yes/no): ").strip().lower()

        if answer == "yes":
            score += 1
            skill_results[skill] = "Known"
        else:
            skill_results[skill] = "Needs Improvement"

    print("\nAssessment completed!")
    print("Your score:", score, "/", len(skills))
    print("\nSkill Analysis:")

    for skill, status in skill_results.items():
        print("-", skill, "→", status)

    return skill_results


def find_skill_gaps(skill_results):
    skill_gaps = []

    for skill, status in skill_results.items():
        if status == "Needs Improvement":
            skill_gaps.append(skill)

    return skill_gaps


if __name__ == "__main__":
    test_skills = ["HTML", "CSS", "JavaScript", "Git & GitHub", "React"]
    results = start_assessment(test_skills)
    skill_gaps = find_skill_gaps(results)

    print("\nSkill Gaps:")
    for skill in skill_gaps:
        print("-", skill)