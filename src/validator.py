years = [2014, 2015, 2016, 2017, 2018]
LENGTHS = {
    "regions": [2, 255],
    "univs": [8, 65535],
    "knowledge_areas": [4, 255]
}

DEFIENED_VALUES = {
    'type': ['gov_exams', 'school_score']
}

ERRORS = {
    'check_min_length': 'value is too short',
    'check_max_length': 'value is too long',
    'field_missing': 'field is required. Field in missing in  request',
    'check_boolean': 'field must be boolean ("true"/"false")',
    'unknown_value': 'Cannot recognize field value'
}


def check_filtering_post_request(data):
    status = {'status': True, 'error': []}
    keys = ['filters',]
    for key in keys:
        if key not in data:
            status['error'].append({key: ERRORS['field_missing']})
    filter_status = check_filtering_params(data['filters'])
    status['error'] += filter_status['error']
    if status['error']:
        status['status'] = False
    return status


def check_filtering_params(data):
    status = {'status': True, 'error': []}
    keys = ['univ_title', 'area_title', 'univ_location', 'year', 'is_enrolled', 'part_top_applicants']
    for key in keys:
        if key == 'univs' or key == 'region' or key == 'knowledge_areas':
            check_min_length_for_array(data, key, status['error'])
            check_max_length_for_array(data, key, status['error'])
        elif key == 'is_enrolled' and (not is_boolean(data[key])):
            status['error'].append({key: ERRORS['check_boolean']})
        elif key == 'part_top_applicants':
            status['error'] += check_part_top_applicants(data[key])
    return status


def check_part_top_applicants(data):
    error = []
    keys = ['type', 'value']
    for key in keys:
        if key not in data:
            error.append({key: ERRORS['field_missing']})
        elif key == 'type' and string_in_range(data[key], DEFIENED_VALUES['type']):
            error.append({key: ERRORS['unknown_value']})
        elif key == 'value' and not int_in_range(data[key], [0, 100]):
            error.append({key: ERRORS['unknown_value']})
    return error


def check_min_length_for_array(data, key, error):
    is_valid_min_length = False not in [check_minimum_length(s, LENGTHS[key][0]) for s in data[key]]
    if not is_valid_min_length:
        error.append({key: ERRORS['check_min_length']})


def check_max_length_for_array(data, key, error):
    is_valid_max_length = False not in [check_maximum_length(s, LENGTHS[key][1]) for s in data[key]]
    if not is_valid_max_length:
        error.append({key: ERRORS['check_max_length']})


def check_minimum_length(string, minimum):
    """Validator function which checks if string is bigger than
       minimum value.
       :params: string - string to check
                minimum - minimal length
    """
    return len(str(string)) >= minimum


def check_maximum_length(string, maximum):
    """Validator function which checks if string is bigger than
       minimum value.
       :params: string - string to check
                minimum - minimal length
    """
    return len(str(string)) <= maximum


def is_boolean(string):
    return string == "true" or string == "false"


def string_in_range(value, range):
    return value in range


def int_in_range(value, range):
    return range[0] <= int(value) <= range[1]
