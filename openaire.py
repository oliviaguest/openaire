import io
import json
import requests
import pandas as pd

refresh_token = open("secret.txt", "r").read()
# get your own from: https://develop.openaire.eu/personal-token

def get_openaire_df(keywords, size):
    # GET https://services.openaire.eu/uoa-user-management/api/users/getAccessToken?refreshToken={your_refresh_token}
    token_response = requests.get('https://services.openaire.eu/uoa-user-management/api/users/getAccessToken?refreshToken=' + refresh_token)
    token_response = json.loads(token_response.content)
    token = 'Bearer {t}'.format(t = token_response['access_token'])
    params = {'keywords': '{t}'.format(t = keywords),
              'format': 'csv',
              'size': size}
    # params = {'keywords': 'category, cognition'} # to be clear, I have no idea what this does!
    # it just seems a sensible starting point!
    # to test it try: https://api.openaire.eu/search/researchProducts?keywords=categorisation,cognition

    response = requests.get("https://api.openaire.eu/search/researchProducts",
                            headers={'Authorization': token},
                            params = params)
    response.raise_for_status()  # raises exception when not a 2xx response
    df = pd.read_csv(io.StringIO(response.content.decode("utf-8")))
    return df


if __name__ == '__main__':
    print(get_openaire_df(keywords='categorisation', size=100))