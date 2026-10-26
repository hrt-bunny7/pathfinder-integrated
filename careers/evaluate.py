from career_recommendation import recommend_careers

examples = [
    {"skills": ["Python", "SQL", "Pandas", "Statistics", "Machine Learning"]},
    {"skills": [{"name": "HTML"}, {"name": "CSS"}, {"name": "JavaScript"}, {"name": "React"}]},
    {"skills": ["Linux", "Networking", "Docker", "Kubernetes", "CI/CD"]},
]

for index, profile in enumerate(examples, start=1):
    print(f"\nExample {index}")
    for career in recommend_careers(profile, top_k=3):
        print(f'{career["role"]}: {career["fit"]}/100')
        print(f'  {career["reason"]}')
