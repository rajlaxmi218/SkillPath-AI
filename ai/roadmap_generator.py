def generate_roadmap(career, skill_results):
    roadmap_lines = []
    week = 1

    for skill, status in skill_results.items():
        if status == "Needs Improvement":
            roadmap_lines.append(f"Week {week}: Learn {skill} (from basics)")
            week += 1
        else:
            roadmap_lines.append(f"Quick Review: {skill} (you already know this - light revision only)")

    roadmap_lines.append(f"Estimated learning duration: {week - 1} week(s), plus quick reviews.")

    for line in roadmap_lines:
        print(line)

    return roadmap_lines