import json

from flask import Flask, request, Response

import validator
from db_pool.db import DBPool
# start application
from utils import FILTER_PARAMS

app = Flask(__name__)
db = DBPool('192.168.163.132', 27017)
db.connect()


@app.route('/', methods=['GET'])
def get_filtering_params():
    knowledge_areas = db.get_knowledge_areas()
    print(knowledge_areas)
    regions = db.get_regions()
    university_titles = db.get_university_titles()
    response_dict = {
        "tags": FILTER_PARAMS,
        "area_title": knowledge_areas,
        "univ_location": regions,
        "univ_title": university_titles
    }
    return Response(json.dumps(response_dict),
                    mimetype='application/json')


@app.route('/', methods=['POST'])
def filter_data_and_analyse():
    data = request.get_json()
    is_valid = validator.check_filtering_post_request(data)
    if not is_valid['status']:
        return Response(json.dumps(is_valid['error']), mimetype='application/json')
    regions = db.get_regions(data)
    return Response(json.dumps(regions), mimetype='application/json')


if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=8080)
