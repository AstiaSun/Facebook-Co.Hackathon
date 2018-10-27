from flask import Flask, render_template, request

import validator
from db_pool.db import DBPool

# start application

app = Flask(__name__)
db = DBPool('192.168.163.132', 27017)
db.connect()


@app.route('/', methods=['GET'])
def get_filtering_params():
    knowledge_areas = db.get_knowledge_areas()
    regions = db.get_regions()
    university_titles = db.get_university_titles()
    print(knowledge_areas)
    print(regions)
    # TODO: send univ titles with ids, knowledge areas, regions to front
    return render_template('hello.html')


@app.route('/', methods=['POST'])
def filter_data_and_analyse():
    data = request.get_json()
    is_valid = validator.check_filtering_post_request(data)
    if is_valid['status']:
        filters = data["filters"]
        # TODO: return filtered requests with analysis
        print(filters)
    else:
        return is_valid['error']
    return "hello"


if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=8080)
