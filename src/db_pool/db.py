from pymongo import MongoClient

from utils import FILTER_KEYS


class DBPool(object):
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._db = None

    def connect(self):
        client = MongoClient(self._host, self._port)
        self._db = client['test']

    def get_university_titles(self):
        return list(self._db.univs.find({}, {'_id': 0, 'univ_title': 1}))

    def get_knowledge_areas(self):
        return list(self._db.areas.find({}, {'area_title': 1}).distinct('area_title'))

    @staticmethod
    def __remove_none_from_list__(values):
        return [x for x in values if x is not None]

    def get_regions(self):
        values = list(self._db.univs.find({}, {'univ_location': 1}).distinct('univ_location'))
        return DBPool.__remove_none_from_list__(values)

    def get_regions(self, filter_data):
        filter_data = self.__format_filter_data_to_mongo_request__(filter_data)
        print(filter_data)
        return list(self._db.areas.find(filter_data))

    def __format_filter_data_to_mongo_request__(self, data):
        result_query = {}
        for key in FILTER_KEYS:
            sub_keys = []
            if isinstance(key, dict):
                key_value = next(iter(key))
                sub_keys = key[key_value]
                key = key_value
            if key in data:
                if key == 'part_top_applicants':
                    for sub_key in sub_keys:
                        result_query[key + '.' + sub_key] = data[key][sub_key]
                elif key == 'is_enrolled':
                    result_query[key] = data[key]
        return result_query
