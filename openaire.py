import pandas as pd
import json
import xmltodict
import requests
from xml.etree import ElementTree

refresh_token = open("secret.txt", "r")
# get your own from: https://develop.openaire.eu/personal-token

def get_inner_data(middle_data, inner_data_key, inner_data_value):
    if type(middle_data) is str:
        # it is just a string
        return middle_data
    elif type(middle_data) is list:
        # it is a list of dicts
        for data_dict in middle_data:
            # print(middle_data)
            if inner_data_value in data_dict.values():
                return data_dict[inner_data_key]
                # return data 
    elif type(middle_data) is dict:
        #  it is just a dict
        return middle_data[inner_data_key]


def get_inner_col(json_dict, middle_data_key, inner_data_key, inner_data_value):
    col_data = []
    for i, item in enumerate(json_dict):
        item = item['metadata']['oaf:entity']['oaf:result']
        try:
            middle_data = item[middle_data_key]
            data = get_inner_data(middle_data, inner_data_key, inner_data_value)
        except KeyError:
            # missing data
            data = ''
        col_data.append(data)
    return col_data


def get_openaire_df(keywords):
    # refresh_token = load it somehow 

    # GET https://services.openaire.eu/uoa-user-management/api/users/getAccessToken?refreshToken={your_refresh_token}
    token_response = requests.get('https://services.openaire.eu/uoa-user-management/api/users/getAccessToken?refreshToken=' + refresh_token)
    token_response = json.loads(token_response.content)
    token = 'Bearer {t}'.format(t = token_response['access_token'])
    params = {'keywords': '{t}'.format(t = keywords)}
    # params = {'keywords': 'category, cognition'} # to be clear, I have no idea what this does! it just seems a sensible starting point!
    # to test it try: https://api.openaire.eu/search/researchProducts?keywords=categorisation,cognition

    response = requests.get("https://api.openaire.eu/search/researchProducts",
                            headers={'Authorization': token},
                            params = params)
    response.raise_for_status()  # raises exception when not a 2xx response

    decoded_response = response.content.decode('utf-8')
    response_json = json.loads(json.dumps(xmltodict.parse(response.content)))
    json_dict = response_json['response']['results']['result']

    middle_data_keys = ['title', 'pid', 'creator', 'dateofacceptance', 'journal']
    # the problem with creator is I am only saving the first author
    inner_data_keys = ['#text', '#text', '#text', '', '#text']
    inner_data_values = ['main title', 'doi', '1', '', '']
    data_zip = zip(middle_data_keys, inner_data_keys, inner_data_values)
    df_dict = {}
    for middle_data_key, inner_data_key, inner_data_value in data_zip:
        df_dict[middle_data_key] = get_inner_col(json_dict, middle_data_key, inner_data_key, inner_data_value)
    
    return pd.DataFrame.from_dict(df_dict)



if __name__ == '__main__':

    print(get_openaire_df(keywords='category, cognition'))