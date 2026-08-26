import pandas as pd

from backend.database import connect_database


# ==== 讀取比賽資料 ====
def load_match_data():

    # Connect to MySQL database
    connection = connect_database()
    cursor = connection.cursor()

    print("Mysql Connection Success")

    # Read all match records from MySQL
    sql = """
        SELECT *
        FROM matches
    """

    cursor.execute(sql)

    # Get column names and query result
    column_names = cursor.column_names
    match_data = cursor.fetchall()

    # Convert MySQL query result to Pandas DataFrame
    match_df = pd.DataFrame(
        match_data,
        columns=column_names
    )

    # Convert match_date to Pandas datetime type
    match_df["match_date"] = pd.to_datetime(
        match_df["match_date"]
    )

    # Close database resources after reading data
    cursor.close()
    connection.close()

    return match_df


# ==== 讀取球隊資料 ====
def load_team_data():

    # Connection to Mysql database
    connection = connect_database()
    cursor = connection.cursor()

    # Read all team records from MySQL
    sql = """
        SELECT *
        FROM team
    """

    cursor.execute(sql)

    # Get column names and query result
    column_names = cursor.column_names
    team_data = cursor.fetchall()

    # Convert Mysql query result to Pandas DataFrame
    team_df = pd.DataFrame(
        team_data,
        columns = column_names
    )

    # Close database resources after reading data
    cursor.close()
    connection.close()


    return team_df
