from pymongo import MongoClient

from utils import FILTER_KEYS, get_some_id


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

    def __get_area_id_by_title__(self, title):
        return self._db.areas.find({"area_title": title}, {"_id": 1})

    def get_regions(self):
        values = list(self._db.univs.find({}, {'univ_location': 1}).distinct('univ_location'))
        return DBPool.__remove_none_from_list__(values)

    def get_regions_by_filter(self, filter_data):
        print(filter_data)
<<<<<<< HEAD
        filter_data = self.__format_filter_data_to_mongo_request__(filter_data)
        #print(filter_data)
        print('result:',filter_data)
        resulting_data = self._db.requests.find(filter_data, {"_id": 0})
        #resulting_data.agregate()
=======
        resulting_data = self._db.requests.find(filter_data, {"_id": 0})
>>>>>>> b9bda33a7bebdb308c09b95db87f322863302d0c
        return list(resulting_data)

    def __format_filter_data_to_mongo_request__(self, data):
        result_query = {}
        for key in FILTER_KEYS:
            if isinstance(key, dict) or key == 'univ_location':
<<<<<<< HEAD
                print(isinstance(key, dict), key)
                continue
            if key in data:
                print(key)
                if key == 'univ_title':
                    if 'univ_location' in data:
=======
                continue
            if key in data:
                if key == 'univ_title':
                    if 'univ_locations' in data:
>>>>>>> b9bda33a7bebdb308c09b95db87f322863302d0c
                        univ_ids = self.__get_univ_ids__(data[key], data['univ_location'])
                    else:
                        univ_ids = [get_some_id(title) for title in data[key]]
                    if len(univ_ids) > 0:
                        result_query['univ_id'] = {"$in": univ_ids}
<<<<<<< HEAD
                    print('univ_ids:',univ_ids)
=======
>>>>>>> b9bda33a7bebdb308c09b95db87f322863302d0c
                elif key == 'area_title':
                    result_query['area_id_old'] = {"$in": [get_some_id(title) for title in data[key]]}
                else:
                    if key == 'is_enrolled':
                        result_query[key] = data[key] == 'true'
                    else:
                        result_query[key] = {"$in": data[key]}
        return result_query

    def __get_univ_ids__(self, title, locations):
        return list(self._db.univs.find({'univ_title': {"$in": title}, 'univ_location': {"$in": locations}},
                                        {"univ_id": 1}).distinct('univ_id'))

    def get_university_title_by_id(self, univ_id):
<<<<<<< HEAD
        return list(self._db.univs.find({"univ_id": univ_id}, {"_id": 0, "univ_id": 1}).dictinct("univ_id"))
=======
        return list(self._db.univs.find({"univ_id": univ_id}, {"_id": 0, "univ_id": 1}).dictinct("univ_id"))
>>>>>>> b9bda33a7bebdb308c09b95db87f322863302d0c
