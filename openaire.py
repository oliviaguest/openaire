import json
import os
import requests
from dotenv import load_dotenv
from lxml import html


load_dotenv(".env")
# get your own from: https://develop.openaire.eu/personal-token
refresh_token = os.getenv("OPENAIRE_REFRESH")


def get_openaire_sample(keywords, size=10_000, page=1):
    # GET https://services.openaire.eu/uoa-user-management/api/users/getAccessToken?refreshToken={your_refresh_token}
    token_response = requests.get('https://services.openaire.eu/uoa-user-management/api/users/getAccessToken?refreshToken=' + refresh_token)
    token_response = json.loads(token_response.content)
    token = 'Bearer {t}'.format(t = token_response['access_token'])
    params = {'keywords': '{t}'.format(t = keywords),
             'format': 'xml',
             'size': size,
             'page': page}
    # to test it try: https://api.openaire.eu/search/researchProducts?keywords=categorization,cognition&format=xml

    response = requests.get("https://api.openaire.eu/search/researchProducts",
                            headers={'Authorization': token},
                            params = params)
    response.raise_for_status()  # raises exception when not a 2xx response

    tree = html.fromstring(response.content)
    n_results = tree.xpath("//total")[0].text

    return response.content, n_results


def parse_openaire_tree(tree):
    """ """
    out = list()
    result_tree = tree.findall(".//results/result")
    for result in result_tree:
        try:
            title = result.find('.//oaf:result/title[@classid="main title"]').text
        except AttributeError:
            title = ""
        try:
            publisher = result.find('.//publisher').text
        except AttributeError:
            publisher = ""
        try:
            author_list = [author.text for author in result.findall(".//creator")]
        except AttributeError:
            author_list = list()

        out.append({
            "title": title,
            "description": "",
            "journal": "",
            "doi": "",
            "publisher": publisher,
            "author_list": author_list,
            "publication_year": "",
            "publication_date": "",
            "funding": "",
            }
            )

    return out

if __name__ == '__main__':
    openaire_data, n = get_openaire_sample(keywords='categorization,cognition', size=20, page=1)
    print(f"Results found: {n}")
    with open('openaire.xml', 'w') as f:
        print(openaire_data.decode("utf-8"), file=f)
    openaire_tree = html.fromstring(openaire_data)
    openaire_sample = parse_openaire_tree(openaire_tree)
    for publication in openaire_sample:
        print("\n")
        for tag, value in publication.items():
            print(f'{tag}: {value}')