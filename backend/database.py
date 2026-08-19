import os
import mysql.connector
from dotenv import load_dotenv


load_dotenv()


# ============================
# Database Connection
# ============================

def connect_database():

    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
        )

    return connection

# ============================
# Save Team Data
# ============================

def save_team_data(cursor, clean_team_data):

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

    print("Team INSERT Success")


# ============================
# Save Competition Data
# ============================

def save_competition_data(cursor, clean_competition_data):

    competition_sql = """
    INSERT INTO competition (
        fifa_competition_id,
        competition_name
    )
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE
        competition_name = VALUES(competition_name)
    """

    for competition in clean_competition_data:

        competition_values = (
            competition["fifa_competition_id"],
            competition["competition_name"]
        )

        cursor.execute(competition_sql, competition_values)

    print("Competition INSERT Success")


# ============================
# Save Match Data
# ============================

def save_match_data(cursor, clean_match_data):

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
    VALUES (%s, %s, %s, %s, %s, %s, %s)
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

    print("Match INSERT Success")
