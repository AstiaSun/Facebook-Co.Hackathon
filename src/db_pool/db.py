from pymongo import MongoClient


class DBPool(object):
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._db = None

    def connect(self):
        client = MongoClient(self._host, self._port)
        self._db = client['test']

    def get_university_titles(self):
        return self._db.univs.find({}, {'univ_id': 1, 'univ_title': 1})

    def get_knowledge_areas(self):
        return self._db.areas.distinct('area_type')

    def get_regions(self):
        return self._db.univs.find({}, {'univ_location': 1}).distinct('univ_location')
