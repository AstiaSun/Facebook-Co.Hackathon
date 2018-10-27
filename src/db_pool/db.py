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
        return list(self._db.univs.find({}, {'_id': 0, 'univ_id': 1, 'univ_title': 1}))

    def get_knowledge_areas(self):
        return list(self._db.areas.find({}, {'_id': 0, 'area_title': 1}).distinct('area_title'))

    @staticmethod
    def __remove_none_from_list__(values):
        return [x for x in values if x is not None]

    def get_regions(self):
        values = list(self._db.univs.find({}, {'univ_location': 1}).distinct('univ_location'))
        return DBPool.__remove_none_from_list__(values)
