import requests

#============================
# API Setting
#============================

MATCH_URL = "https://inside.fifa.com/api/data-centre/matches?gender=1&year=2022&language=en&count=25"
TEAM_URL = "https://inside.fifa.com/api/data-centre/matches/teams?gender=1&language=en&year=2022"


HEADERS = {

    "Accept": "application/json, text/plain, */*",
    "Accept-language": "en-US,en;q=0.9",
    "Referer": "https://inside.fifa.com/data-centre/matches/men?year=2022",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
}

def get_match_data():

    match_response = requests.get(
        
        MATCH_URL,
        headers=HEADERS
    )

    match_data = match_response.json()

    return match_data


def get_team_data():

    team_response = requests.get(

        TEAM_URL,
        headers=HEADERS
    )

    team_data = team_response.json()

    return team_data





