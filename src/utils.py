import base64

FILTER_PARAMS = {'univs': "Університет", 'knowledge_areas': "Галузь знань", 'years': "Рік",
                 'part_top_applicants.value': "ТОП студентів(%)", 'regions': "Регіон",
                 'type.gov_exams': "По балам ЗНО", 'type.school_score': "По балам атестату"}
FILTER_KEYS = ['univ_title', 'area_title', {'part_of_applicants': ["type", "value"]}, "univ_location", "year", "is_enrolled"]

def get_some_id(univ_title):
    return base64.b64encode(univ_title.encode('utf-8')).decode('ascii')