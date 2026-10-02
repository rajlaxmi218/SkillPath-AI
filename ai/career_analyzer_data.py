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