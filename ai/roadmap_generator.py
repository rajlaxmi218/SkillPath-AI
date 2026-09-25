def generate_roadmap(career, skill_results):
    print(f"\n===== Personalized Roadmap for {career} =====\n")

    week = 1

    for skill, status in skill_results.items():
        if status == "Needs Improvement":
            print(f"Week {week}: Learn {skill} (from basics)")
            week += 1
        else:
            print(f"Quick Review: {skill} (you already know this — light revision only)")

    print(f"\nEstimated learning duration: {week - 1} week(s), plus quick reviews.")