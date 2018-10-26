
# coding: utf-8

# In[1]:


import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import json
import re


# In[84]:


class request():
    def __init__(self):
        self.Name = ""
        self.Ranking = 0
        self.Surname = ""
        self.Given_name = ""
        self.Total_score = 0
        
        self.School_score = 0
        self.Gov_exams = {}
        self.Univ_exams = {}
        self.Extra_points = {}
        
        self.Is_out_of_competition = False
        #for comp. with 2014 data
        self.Is_prioritized = False
        #for comp. with 2014 data
        self.Is_directed = False
        
        self.Is_original = False
        self.Is_enrolled = False
        self.Priority = 0
        self.Status = ""


# In[85]:


subj_mapping = {"Математика" : "math", "Українська мова та література" : "ukr",
                "Іноземна мова" : "foreign", "Фізика" : "phys", "Хімія" : "chem", 
                "Біологія" : "bio", "Географія" : "geo", "Англійська мова" : "eng", 
                "Історія України" : "ukr_hist", "Фахове випробування" : "profile_exam", "Російська мова" : "rus",
                "Творчий конкурс" : "art"}


# In[86]:


def parse_details(src):
    school_score = 0
    try:
        school_score = float(re.search("Середній бал документа про освіту: ([0-9]*\.[0-9]+|[0-9]+)", src).group(1))
    except AttributeError:
        pass
    extra_points = {}
    try:
        extra_points["Olimpiads"] = int(re.search("Бал за особливі успіхи : ([0-9]*\.[0-9]+|[0-9]+)", src).group(1))
    except AttributeError:
        pass
    gov_exams = {}
    for item in subj_mapping.keys():
        try:
            gov_exams[subj_mapping[item]] = int(re.search(str(item) + " \(ЗНО\): ([0-9]*)", src).group(1))
        except AttributeError:
            pass
    univ_exams = {}
    for item in subj_mapping.keys():
        try:
            univ_exams[subj_mapping[item]] = int(re.search(str(item) + " \(іспит\): ([0-9]*)", src).group(1))
        except AttributeError:
            pass
        try:
            univ_exams[subj_mapping[item]] = int(re.search(str(item) + ": ([0-9]*)", src).group(1))
        except AttributeError:
            pass
    return school_score, gov_exams, univ_exams, extra_points


# In[153]:


def html_2018_to_parsed_json(src):
    soup = bs(src,'html.parser')
    tab=soup.find("table", {"class":"tablesaw tablesaw-stack tablesaw-sortable"})
    df = pd.read_html(str(tab), skiprows=0)[0]
    res = []
    for index, row in df.iterrows():
        r = request()
        r.Name, r.Surname, r.Given_name = (row['ПІБ'] + ' - - ').split(' ')[:3]
        r.Total_score = row['Σ']
        r.Priority = row['П']
        r.Status = str(row['С'])
        r.Ranking = row['#']
        r.Is_enrolled = (str(row["С"])[:9] == "До наказу")
        r.Is_out_of_competition = (str(row['К']) != "—")
        r.Is_original = (str(row['Д']) == "+")
        r.School_score, r.Gov_exams, r.Univ_exams, r.Extra_points = parse_details(row['Деталізація'])
        res.append(json.dumps(r.__dict__))
    return res

