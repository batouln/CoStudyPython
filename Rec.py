# needed packages
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
    "problem-solving", "UI/UX Design", "game development", "theoretical computer science","Analytical Thinking"
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

# items >> our courses

def rec(updated_portfolio, inter,online_courses_list,UserId):
    user_vector = [0] * len(All_Skills)
    user_skills = []

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

            # eliminate the zero vectors
            if any(item_vector):
                final_result.append({"name": item["title"], "vector": item_vector})

    # eliminate missed_pre items if their missed count = 0 (no pre skill missed)
    new_missed_pre = {}

    for item, count in missed_pre.items():
        if count != 0:
            new_missed_pre[item] = count

    missed_pre = new_missed_pre

    item_vectors = [item["vector"] for item in final_result]

    # Calculate cosine similarity between user vector and item_vectors
    item_similarities = cosine_similarity(item_vectors, [user_vector]).flatten()

    average_similarity = np.mean(item_similarities)

    # Adjust similarities for items in missed_pre
    missed = [i for i, item in enumerate(final_result) if item["name"] in missed_pre]
    if missed:
        for index in missed:
            missed_count = missed_pre[final_result[index]["name"]]  # Get the missed count for the item
            similarity_adjustment = missed_count * average_similarity * 0.3  # Adjust the similarity by multiplying with a factor (e.g., 0.1)
            item_similarities[index] = item_similarities[index] - item_similarities[index] * similarity_adjustment

    

    # Sort the items based on similarity
    sorted_indices = np.argsort(item_similarities)[::-1]  # Sort in descending order
    sorted_items = [final_result[i]["name"] for i in sorted_indices]

    # to print
    similars = {}

    # Print sorted items and their similarity scores
    for item, similarity in zip(sorted_items, item_similarities[sorted_indices]):
        similars[item] = similarity

    interests = [0] * len(All_Skills)

    for i, skill in enumerate(All_Skills):
        if skill in inter:
            interests[i] = 1

    choosen = []

    for title, similarity in zip(sorted_items, item_similarities[sorted_indices]):
        covered_skills = next((item for item in items if item["title"] == title), {}).get("covered", [])  # get the covered skills of the item

        item_skills = [0] * len(All_Skills)

        for i, skill in enumerate(All_Skills):
            if skill in covered_skills and skill in inter:
                item_skills[i] = 1

        choosen.append({"title": title, "vector": item_skills})

    # Compute cosine similarity
    similarities = cosine_similarity([vector["vector"] for vector in choosen], [interests])
    similarities = similarities.flatten()

    # Create a dictionary to store the similarities with indices
    similarities_dict = {i: similarity for i, similarity in enumerate(similarities)}

    # Sort by similarity in descending order
    sorted_items_2 = sorted(choosen, key=lambda x: similarities_dict[choosen.index(x)], reverse=True)

    results_dict = {}

    for item in sorted_items_2:
        title = item["title"]
        similarity = similarities_dict[choosen.index(item)]
        results_dict[title] = similarity

    for title, similarity in similars.items():
        if title in results_dict:
            similarity = similarity + (similarity * results_dict[title])
            similars[title] = similarity

    sorted_similars = sorted(similars.items(), key=lambda item: item[1], reverse=True)
    sorted_similars = {title: similarity for title, similarity in sorted_similars}

    beginners = [item for item in items if item["title"] in no_pre_list]
    covered_skills = []
    choosen2 = []

    for item in beginners:
        covered_skills = item['covered']
        item_skills = [0] * len(All_Skills)
        
        for i, skill in enumerate(All_Skills):
            if skill in covered_skills and skill in inter:
                item_skills[i] = 1

        if any(item_skills):
            choosen2.append({"title": item["title"], "vector": item_skills})

    w = False

    if len(choosen2):
        similarities2 = cosine_similarity([vector["vector"] for vector in choosen2], [interests])
        similarities2 = similarities2.flatten()

        # Create a dictionary to store the similarities with indices
        similarities_dict2 = {i: similarity for i, similarity in enumerate(similarities2)}

        # Sort by similarity in descending order
        sorted_items_3 = sorted(choosen2, key=lambda x: similarities_dict2[choosen2.index(x)], reverse=True)

        results_dict2 = {}

        for item in sorted_items_3:
            title = item["title"]
            similarity = similarities_dict2[choosen2.index(item)]
            results_dict2[title] = similarity

        combined = {**results_dict2, **sorted_similars}
        sorted_combined = sorted(combined.items(), key=lambda item: item[1], reverse=True)
        sorted_combined = {title: similarity for title, similarity in sorted_combined}
        w = True
    else:
        Final = sorted_similars

    from itertools import islice

    n = 5

    if w:
        recommended_courses = list(islice(sorted_combined.keys(), n))
    else:
        recommended_courses = list(islice(Final.keys(), n))

    RecommendedCourses=[]
    missed_preq=list(missed_pre.keys())
    #get the ids first
    for rec in recommended_courses:
        for item in items:
            if rec==item['title']:
                if int(item["id"]) not in online_courses_list:
                    r={}
                    Flag=0
                    r.setdefault("UserId", UserId)
                    r.setdefault("OnlineCourseId",int(item["id"]))
                    if rec in missed_preq:
                        Flag=1
                    r.setdefault("Flag",Flag)
                    RecommendedCourses.append(r)
    return RecommendedCourses
