import csv
from ast import literal_eval
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# Needed Data
All_Skills = [
    "C++", "C", "C#", "Java", "Javascript", "python", "ruby", "R", "php", "Matlab", "prolog", "Haskell",
    "frontend development", "backend development", "APIs", "Database management", "Netwroking",
    "Data analysis", "Data Engineering", "Cloud computing and Distributed systems", "Cybersecurity",
    "Mobile development", "software engineering", "software development", "Design Patterns",
    "Quality Assurance and Testing", "Computer architecture", "Mathematics", "Artificial intelligence",
    "machine learning", "deep learning", "Natural language processing", "image processing and computer vision",
    "problem-solving", "UI/UX Design", "game development", "theoretical computer science"
]

skill_level = {
    "beginner": 0.05,
    "intermediate": 0.3,
    "advanced": 0.5
}

# this is from the first stage >> user_portfolio it's a dict {"skill": scale} + interests list
# this function should return a list of dicts, each dict will contain {"userid", "courseid", "flag"}

# creating item profiles (id, titles, pre, covered, level)
# since we return ids to ASP.NET, the final set from rec code is going to be title and then I will retrieve its ID

filename = "C:/Users/Batoul/Downloads/finalcoursesWithId.csv"
keynames = ["Id", "Title", "Prerequisites_List", "Covered_List", "Level"]
itemnames = ["id", "title", "pre_skills", "covered", "level"]
items = []

with open(filename, "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        data = {}
        for i in range(0, len(keynames)):
            if keynames[i] == "Prerequisites_List" or keynames[i] == "Covered_List":
                data[itemnames[i]] = literal_eval(row[keynames[i]])
            else:
                data[itemnames[i]] = row[keynames[i]]
        items.append(data)

user_vector = [0] * len(All_Skills)
user_skills = []
updated_portfolio={'python': 0.7,
 'frontend development': 0.7749999999999999,
 'Cloud computing and Distributed systems': 0.25,
 'Database management': 0.4375,
 'backend development': 0.25,
 'Data Engineering': 0.25,
 'Data analysis': 0.4375,
 'software engineering': 0.25}

for k in updated_portfolio.keys():
    user_skills.append(k)
for i, skill in enumerate(All_Skills):
        for u in user_skills:
            if u==skill:
                user_vector[i]=updated_portfolio[u]
missed_pre = {}
final_result = []
no_pre_list = []

for item in items:
    if "No Prerequisites" == item["pre_skills"][0]:
        no_pre_list.append(item["title"])
    else:
        item_vector = [0] * len(All_Skills)
        missed_count = 0  # Counter for missed skills
        for i, skill in enumerate(user_vector):
            if All_Skills[i] in item["pre_skills"]:
                 if user_vector[i] == 0:
                    missed_count += 1
                 elif skill_level[item["level"]] <= updated_portfolio[All_Skills[i]]:
                    item_vector[i] = skill_level[item["level"]]
                 elif skill_level[item["level"]] > updated_portfolio[All_Skills[i]]:
                    item_vector[i] = skill_level[item["level"]]
                    missed_count += 1

        missed_pre[item["title"]] = missed_count
        print(item_vector)

            # eliminate the zero vectors
        if any(item_vector):
            final_result.append({"name": item["title"], "vector": item_vector})

new_missed_pre = {}
for item, count in missed_pre.items():
    if count != 0:
        new_missed_pre[item] = count
missed_pre = new_missed_pre
item_vectors = [item["vector"] for item in final_result]
item_similarities = cosine_similarity(item_vectors, [user_vector]).flatten()

print(item_similarities)