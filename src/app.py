import json

from flask import Flask, request, Response
from flask_cors import CORS

import validator
from db_pool.db import DBPool
# start application
from utils import FILTER_PARAMS
import visualization
app = Flask(__name__)
db = DBPool('192.168.163.132', 27017)
db.connect()
CORS(app)

@app.route('/', methods=['GET'])
def get_filtering_params():
    knowledge_areas = db.get_knowledge_areas()
    #print(knowledge_areas)
    regions = db.get_regions()
    university_titles = db.get_university_titles()
    response_dict = {
        "tags": FILTER_PARAMS,
        "area_title": knowledge_areas,
        "univ_location": regions,
        "univ_title": [x['univ_title'] for x in university_titles]
    }
    response = Response(json.dumps(response_dict),  mimetype='application/json')
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@app.route('/', methods=['POST'])
def filter_data_and_analyse():
    data = request.get_json()
    #is_valid = validator.check_filtering_post_request(data)
    #if not is_valid['status']:
    #    return Response(json.dumps(is_valid['error']), mimetype='application/json')
    print(data)
    regions = db.get_regions_by_filter(data['filters'])
    #print(regions)
    jsn = json.dumps(regions)
    tk = list(data['filters'].keys())

    if len(tk) != 1 or tk[0] != 'area_title':
        chart = visualization.draw_piechart(jsn, grouping_threshold = 0.1)
    else:
        print('very experimental feature')
        chart = visualization.draw_hist(jsn, column='course_id', grouping_threshold = 0.1)
    #return Response(, mimetype='application/json')
    response = Response(b'<img src="' + chart + b'"/>', mimetype='application/html')
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


if __name__ == '__main__':

    app.debug = True
    app.run(host='0.0.0.0', port=8080)
