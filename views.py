import json
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import csv
import pandas as pd
from ast import literal_eval
from .Rec import rec
@csrf_exempt
def Update_Portfolio(request):
    if request.method == 'POST':
        try:
            #weights
            book_weight = 0.15
            uni_course = 0.6
            online_course = 0.25
            grades = {'A': 90, 'A-': 90, 'B+': 80, 'B': 80, 'B-': 75, 'C+': 60, 'C': 60, 'C-': 55, 'D+': 50, 'D': 40}
            skills_csv=pd.read_csv("C:/Users/Batoul/Downloads/skills.csv")#here we have id's with labels
            books=pd.read_csv("C:/Users/Batoul/Downloads/BooksSkills.csv")
            #Extract data from the JSON request
            user_skills = json.loads(request.body)
            UserId = user_skills["UserId"]
            uni_courses_list = user_skills["UniCourses"]
            #Flags for handling empty string (OnlineCoursesIds) , (Books):
            book_flag=True
            online_flag=True
            #Book Skills
            if(len(user_skills["Books"])==0):
               book_flag=False
            if(book_flag):
                books_ids__list = user_skills["Books"].split(",")
                books_ids__list =[int(i) for i in books_ids__list]
                books_skills=[]
                for book in books_ids__list:
                    books_skills += literal_eval(books.loc[books['Id'] == int(book), 'Covered_List_2'].values[0])

            if(len(user_skills["OnlineCoursesIds"])==0):
                online_flag=False
            

            interests_ids_list = user_skills["Interests"].split(",")
            interests_ids_list=[int(i) for i in interests_ids_list]
            interests_list=[skills_csv.loc[skills_csv['id']==i,"skill"].values[0] for i in interests_ids_list]

            #Extract skills from online courses
            online_courses_list=[]
            if(online_flag):
                online_courses_list = user_skills["OnlineCoursesIds"].split(",")
                online_courses_list=[int(i) for i in online_courses_list]
                online_courses_skills = []
                onlineCourses = pd.read_csv("C:/Users/Batoul/Downloads/finalcoursesWithId.csv")
                for online in online_courses_list:
                    online_courses_skills += literal_eval(onlineCourses.loc[onlineCourses['Id'] == int(online), 'Covered_List'].values[0])
            
            


            #Extract the current portfolio
            portfolio = user_skills["CurrentPortfolio"]
            updated_portfolio = {}
            for dict in portfolio:
                label=skills_csv.loc[skills_csv['id']==int(dict["SkillId"]),"skill"].values[0]
                updated_portfolio.setdefault(label, dict["Scale"])

            #Calculate updated portfolio based on weights and skills
            #Online Courses Weight
            if(online_flag):
                for skill in online_courses_skills:
                    updated_portfolio.setdefault(skill, 0)
                    add = online_course * (1 - updated_portfolio[skill])
                    updated_portfolio[skill] += add
            #books&uni weights
            if(book_flag):
                for skill in books_skills:
                    updated_portfolio.setdefault(skill,0)
                    add=book_weight * (1 - updated_portfolio[skill])
                    updated_portfolio[skill]+=add 

            #Extract UniCourses +Grade+weights:
            #list of dicts
            uni_courses=pd.read_csv("C:/Users/Batoul/Downloads/UniSkills.csv")          
            for uni in uni_courses_list:
                grade=grades[uni['Grade']]
                uni_str=uni_courses.loc[uni_courses['id'] == int(uni["CourseId"]), 'skills'].values[0]
                uni_skills=uni_str.split(",")
                for skill in uni_skills:
                    updated_portfolio.setdefault(skill,0)
                    add=uni_course * (grade / 100) * (1 - updated_portfolio[skill])
                    updated_portfolio[skill] += add

            #Prepare the response with the updated portfolio
            NewPortfolio = []
            for key, value in updated_portfolio.items():
                p = {}
                p.setdefault("UserId", UserId)
                SkillId=skills_csv.loc[skills_csv['skill']==key,"id"].values[0]
                p.setdefault("SkillId", int(SkillId))
                p.setdefault("Scale", round(value, 2))
                NewPortfolio.append(p)

            data = {}
            rec_result=rec(updated_portfolio,interests_list,online_courses_list,UserId)
            data.update({"UpdatedPorfolio": NewPortfolio})
            data.update({"RecommendedCourses": rec_result})
            return JsonResponse(data)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
