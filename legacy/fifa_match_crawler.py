import os
import requests
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

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

#============================
# Database
#============================

def connect_database():

    connection = mysql.connector.connect(
        host = os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    
    return connection

#============================
# Debug
#============================

def watch_match_get(match_response, match_data):
    print("==== Match GET ====")

    print("Match Status Code:", match_response.status_code)
    print("Match Response Type:", type(match_response))
    print("Match Data Type:", type(match_data))
    print("\n")


def watch_team_get(team_response, team_data):
    print("==== Team GET ====")

    print("Team Status Code:", team_response.status_code)
    print("Team Response Type:", type(team_response))
    print("Team Data Type:", type(team_data))
    #print("Team: ", team)
    print("\n")

    print("==== Team GET One ====")

    count = 0

    for team in team_data:

        #team = team_data[0]
        team_id = team["id"]
        association_id = team["associationId"]
        team_name = team["name"]
        confederation_id = team["confederation"]["id"]
        confederation_name = team["confederation"]["name"]
        count += 1

        print("Team ID:", team_id)
        print("Association ID:", association_id)
        print("Team Name:", team_name)
        print("Confederation ID:", confederation_id)
        print("Confederation Name", confederation_name)

        print("\n")

    print("Processed Team Count:", count)


def debug_response(team_response):
    print("==== Team Response Debug ====")

    print("Team Status Code:", team_response.status_code)
    print("Team Content-Type:", team_response.headers.get("Content-Type"))
    print("Team Response Type:", type(team_response))
    print("Team Response:", team_response.text[:500])

# ============================
# Test
# ============================

def test_match_data(match_data):

    print("==== Match Data Test ====")

    print("Match Count:", len(match_data))

    for match in match_data:
#---- Prepare Match Data ----
        match_id = match["idMatch"]
        match_date = match["matchDate"]

        team_a_id = match["teamAId"]
        team_b_id = match["teamBId"]

        team_a_score = match["teamAScore"]
        team_b_score = match["teamBScore"]

# ============================
# Test Output
# ============================
        print("Match ID:", match["idMatch"])
        print("Date:", match["matchDate"])
        print("Team A ID:", match["teamAId"])
        print("Team B ID:", match["teamBId"])
        print("Team A Score:", match["teamAScore"])
        print("Team B Score:", match["teamBScore"])
        print("--------")


def test_team_data(team_data):

    print("==== Team Data Test ====")

    print("Team Data Type:", type(team_data))
    print("Team Count:", len(team_data))
    print(team_data[0])
    print("--------")

# ============================
# SQL Input
# ============================

#----SQL team ----
def SQL_team_data(team_data, clean_team_data):

    print("==== SQL Data Input ====")

#將JSON放入變數中，預備丟入SQL
    error_team_data = []
    teamDataCnt = 0

    for team in team_data:

        fifa_team_id = team["id"]
        association_id = team["associationId"]
        team_name = team["name"]
        confederation_id = team["confederation"]["id"]
        confederation_name = team["confederation"]["name"]

        clean_team = {
            "fifa_team_id": fifa_team_id,
            "association_id": association_id,
            "team_name": team_name,
            "confederation_id": confederation_id,
            "confederation_name": confederation_name
        }

        clean_team_data.append(clean_team)
     

    #SQL_count = len(clean_team_data)
    #print("SQL Count:", SQL_count)
    #print("SQL Data:", clean_team_data[:5])
    #print()

#驗證放入的資料欄位有沒有問題
    expected_keys = {
        "fifa_team_id",
        "association_id",
        "team_name",
        "confederation_id",
        "confederation_name"
    }
    
    for team in clean_team_data:
        if set(team.keys()) != expected_keys:
            error_team_data.append(team)
            print("資料欄位異常", team)
        else:
            teamDataCnt += 1
    
    if teamDataCnt == len(clean_team_data): 
        print("資料欄位正常")
    else:
        print("資料欄位異常")
        for team in error_team_data:
            print(team)


    print("==== Clean Team Data Test ====")

    print("Total Team:", len(clean_team_data))

    for team in clean_team_data[:5]:
        print(team)
    

#----SQL Match ----

def SQL_match_data(match_data, clean_match_data):

    print("==== SQL Data Input ====")

#將JSON放入變數中，預備丟入SQL
    error_match_data = []

    for match in match_data:

        fifa_match_id = match["idMatch"]
        match_date = match["matchDate"]
        fifa_competition_id = match["idCompetition"]

        team_a_fifa_id = match["teamAId"]
        team_b_fifa_id = match["teamBId"]

        team_a_score = match["teamAScore"]
        team_b_score = match["teamBScore"]
        

        clean_match = {
            "fifa_match_id": fifa_match_id,
            "match_date": match_date,
            "fifa_competition_id": fifa_competition_id,
            "team_a_fifa_id": team_a_fifa_id,
            "team_b_fifa_id": team_b_fifa_id,
            "team_a_score": team_a_score,
            "team_b_score": team_b_score
        }

        clean_match_data.append(clean_match)

        
    print("Match Count:", len(clean_match_data))
    print("Match Data:", clean_match_data[:5])

    expected_match_keys = {
        "fifa_match_id",
        "match_date",
        "fifa_competition_id",
        "team_a_fifa_id",
        "team_b_fifa_id",
        "team_a_score",
        "team_b_score"
    }

    for match in clean_match_data:

        if set(match.keys()) != expected_match_keys:
            error_match_data.append(match)

    if len(error_match_data) == 0:
        print("Match 資料欄位正常")
    else:
        print("Match 資料欄位異常")

        for match in error_match_data:
            print(match)
    
#---- competition data ----
def SQL_competition_data(match_data, clean_competition_data):

    print("==== SQL Competition Data Input ====")

    seen_competition_ids = set()

    for match in match_data:

        fifa_competition_id = match["idCompetition"]
        competition_name = match["competitionName"][0]["description"]

        if fifa_competition_id not in seen_competition_ids:
            clean_competition = {
                "fifa_competition_id": fifa_competition_id,
                "competition_name": competition_name
            }

            clean_competition_data.append(clean_competition)
            seen_competition_ids.add(fifa_competition_id)

    print("Competition Count:", len(clean_competition_data))
    print("Competition Data:", clean_competition_data[:5])

#---- Watch Team Data Type ----
    # for team in team_data:

    #     team_id = team["id"]
    #     association_id = team["associationId"]
    #     team_name = team["name"]
    #     confederation_id = team["confederation"]["id"]
    #     confederation_name = team["confederation"]["name"]

    #     print("Team ID:", team_id)
    #     print("Team ID Type:", type(team_id))

    #     print("Association ID:", association_id)
    #     print("Association ID Type:", type(association_id))

    #     print("Team Name:", team_name)
    #     print("Team Name Type:", type(team_name))

    #     print("Confederation ID:", confederation_id)
    #     print("Confederation ID Type:", type(confederation_id))

    #     print("Confederation Name:", confederation_name)
    #     print("Confederation Name Type:", type(confederation_name))

    #     break
# ============================
# Main
# ============================
def main():


#---- Database Connection ----
    connection = connect_database()
    cursor = connection.cursor()
    
    print("MySQL Connection Success")

#---- SQL SELECT Test  ----
    cursor.execute("SELECT * FROM team")

    result = cursor.fetchall()

    print("==== SQL SELECT Test ====")
    print(result)

#---- Get Match Data ----
    match_response = requests.get(MATCH_URL, headers = HEADERS)

    match_data = match_response.json()

#---- Get Team Data ----
    team_response = requests.get(TEAM_URL, headers = HEADERS)

    team_data = team_response.json()


#---- SQL Inout ----

    clean_team_data = []
    clean_match_data = []
    clean_competition_data = []

    SQL_team_data(team_data, clean_team_data)
    SQL_match_data(match_data, clean_match_data)
    SQL_competition_data(match_data, clean_competition_data)

#---- SQL INSERT Team Test ----

    #team = clean_team_data[0]

    team_sql = """
    INSERT INTO team (
        fifa_team_id,
        team_name,
        association_id,
        confederation_id,
        confederation_name
    )
    VALUES (%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        team_name = VALUES(team_name),
        association_id = VALUES(association_id),
        confederation_id = VALUES(confederation_id),
        confederation_name = VALUES(confederation_name)
    """
    
    for team in clean_team_data:
        
        values = (
            team["fifa_team_id"],
            team["team_name"],
            team["association_id"],
            team["confederation_id"],
            team["confederation_name"]
        )
 
        cursor.execute(team_sql, values)
    
    connection.commit()

    print("Team INSERT Success")

#---- SQL INSERT Competition ----

    competition_sql = """
    INSERT INTO competition (
        fifa_competition_id,
        competition_name
    )
    VALUE (%s, %s)
    ON DUPLICATE KEY UPDATE
        competition_name = VALUES(competition_name)
    """
    for competition in clean_competition_data:

        competition_values = (
            competition["fifa_competition_id"],
            competition["competition_name"]
        )

        cursor.execute(competition_sql, competition_values)

    connection.commit()

    print("Competition INSERT Success")

#---- SQL INSERT Match Test ----

    #match = clean_match_data[0]

    match_sql = """
    INSERT INTO matches (

        fifa_match_id,
        match_date,
        fifa_competition_id,
        team_a_fifa_id,
        team_b_fifa_id,
        team_a_score,
        team_b_score
    )
    VALUES(%s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        match_date = VALUES(match_date),
        fifa_competition_id = VALUES(fifa_competition_id),
        team_a_fifa_id = VALUES(team_a_fifa_id),
        team_b_fifa_id = VALUES(team_b_fifa_id),
        team_a_score = VALUES(team_a_score),
        team_b_score = VALUES(team_b_score)
    """

    for match in clean_match_data:

        match_values = (
            match["fifa_match_id"],
            match["match_date"],
            match["fifa_competition_id"],
            match["team_a_fifa_id"],
            match["team_b_fifa_id"],
            match["team_a_score"],
            match["team_b_score"]
        )

        cursor.execute(match_sql, match_values)

    connection.commit()

    print("Match INSERT Success")

#---- Close Database Connection ----

    cursor.close()
    connection.close()

# ============================
# Test / Debug
# ============================

    #watch_match_get(match_response, match_data)

    #watch_team_get(team_response, team_data)

    #test_match_data(match_data)

if __name__ == "__main__":
    main()
