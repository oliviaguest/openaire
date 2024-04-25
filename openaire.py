import json
import os
import re
import requests
from dotenv import load_dotenv
from lxml import html


load_dotenv(".env")
refresh_token = os.getenv("OPENAIRE_REFRESH")
# get your own from: https://develop.openaire.eu/personal-token
# https://graph.openaire.eu/docs/apis/authentication


def get_openaire_sample(keywords, size=10_000, page=1):
    # GET https://services.openaire.eu/uoa-user-management/api/users/getAccessToken?refreshToken={your_refresh_token}
    token_response = requests.get(
        "https://services.openaire.eu/uoa-user-management/api/users/getAccessToken?refreshToken="
        + refresh_token
    )
    token_response = json.loads(token_response.content)
    token = "Bearer {t}".format(t=token_response["access_token"])
    params = {
        "keywords": "{t}".format(t=keywords),
        "format": "xml",
        "size": size,
        "page": page,
    }
    # to test it try: https://api.openaire.eu/search/researchProducts?keywords=categorization,cognition&format=xml

    response = requests.get(
        "https://api.openaire.eu/search/researchProducts",
        headers={"Authorization": token},
        params=params,
    )
    response.raise_for_status()  # raises exception when not a 2xx response

    tree = html.fromstring(response.content)
    n_results = tree.xpath("//total")[0].text

    return response.content, n_results


def parse_openaire_tree(tree):
    """ """
    out = list()
    result_tree = tree.findall(".//results/result")
    for result in result_tree:
        if len(result.xpath(".//instancetype/@classname")) > 0:
            instance_type = result.xpath(".//instancetype/@classname")[0]
        else:
            instance_type = "Unknown"
        data_source = result.xpath(".//collectedfrom/@name")[0]
        if len(result.xpath(".//dateofacceptance")) > 0:
            publication_date = result.xpath(".//dateofacceptance")[0].text
        else:
            publication_date = "Unknown"
        publication_year = (
            re.search(r"(\d{4})-\d{2}-\d{2}", publication_date).group(1)
            if re.search(r"(\d{4})-\d{2}-\d{2}", publication_date)
            else None
        )
        if len (result.xpath(".//refereed/@classname")) > 0:
            refereed = result.xpath(".//refereed/@classname")[0]
        urls = [url.text for url in result.xpath(".//webresource/url")]

        if instance_type == "Article":
            try:
                journal = result.find(".//journal").text
            except AttributeError:
                journal = ""
        else:
            journal = None
        try:
            title = result.find('.//oaf:result/title[@classid="main title"]').text
        except AttributeError:
            title = ""
        try:
            alt_title = result.find(
                './/oaf:result/title[@classid="alternative title"]'
            ).text
        except AttributeError:
            alt_title = ""
        try:
            publisher = result.find(".//publisher").text
        except AttributeError:
            publisher = ""
        try:
            author_list = [author.text for author in result.findall(".//creator")]
        except AttributeError:
            author_list = list()
        try:
            doi = result.find('.//pid[@classid="doi"]').text
        except AttributeError:
            doi = ""
        try:
            description = result.find(".//description").text
        except AttributeError:
            description = ""

        out.append(
            {
                "title": title,
                "alternative title": alt_title,
                "description": description,
                "type": instance_type,
                "journal": journal,
                "doi": doi,
                "url": urls,
                "publisher": publisher,
                "authors": author_list,
                "publication_year": publication_year,
                "publication_date": publication_date,
                "funding": "",
                "data source": data_source,
                "refereed": refereed,
            }
        )

    return out


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--page", type=int, default=1, help="Page number")
    parser.add_argument("--size", type=int, default=1, help="Number of results to get")
    parser.add_argument(
        "--keywords",
        type=str,
        nargs="?",
        default="categorization,cognition",
        help="Keyword(s) to search for",
    )
    args = parser.parse_args()

    openaire_data, n = get_openaire_sample(
        keywords=args.keywords, size=args.size, page=args.page
    )
    print(f"Results found: {n}")
    with open("openaire.xml", "w") as f:
        print(openaire_data.decode("utf-8"), file=f)
    openaire_tree = html.fromstring(openaire_data)
    openaire_sample = parse_openaire_tree(openaire_tree)
    for publication in openaire_sample:
        for tag, value in publication.items():
            print(f"{tag}: {value}")
        break
