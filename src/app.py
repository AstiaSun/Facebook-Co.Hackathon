from flask import Flask, render_template

from db_pool.db import DBPool

# start application

app = Flask(__name__)
db = DBPool('192.168.163.132', 27017)
db.connect()


# logger = logging.basicConfig(level=logging.DEBUG)


@app.route('/', methods=['GET'])
def get_filtering_params():
    knowledge_areas = db.get_knowledge_areas()
    regions = db.get_regions()
    university_titles = db.get_university_titles()
    print(knowledge_areas)
    print(regions)
    print(university_titles)
    return render_template('hello.html')


if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=8080)
