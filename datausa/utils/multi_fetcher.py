import requests
from requests.models import RequestEncodingMixin

from config import API
from datausa.utils.format import num_format
from datausa import app


def merge_dicts(*dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def multi_col_top(profile, params):
    attr_type = params.get("attr_type", profile.attr_type)
    rows = params.pop("rows", False)
    params["show"] = params.get("show", attr_type)
    params["limit"] = params.get("limit", 1)
    params["sumlevel"] = params.get("sumlevel", "all")
    params[attr_type] = profile.id
    cols = params.pop("required")
    params["required"] = ",".join(cols)
    namespace = params.pop("namespace")
    query = RequestEncodingMixin._encode_params(params)
    url = "{}/api?{}".format(API, query)
    try:
        r = requests.get(url).json()
    except ValueError:
        app.logger.info("STAT ERROR: {}".format(url))
        return {
            "url": "N/A",
            "value": "N/A"
        }
    if not rows:
        api_data = r["data"][0]
    else:
        api_data = r["data"]
    headers = r["headers"]
    moi = {namespace: {} if not rows else []}

    if not rows:
        for col in cols:
            moi[namespace][col] = num_format(api_data[headers.index(col)], col)
    else:
        for data_row in api_data:
            myobject = {}
            for col in cols:
                myobject[col] = num_format(data_row[headers.index(col)], col)
            moi[namespace].append(myobject)
    return moi
