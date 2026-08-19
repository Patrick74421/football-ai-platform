from fifa_crawler import get_match_data, get_team_data

from data_cleaner import (
    prepare_team_data,
    prepare_match_data,
    prepare_competition_data
)

from database import (
    connect_database,
    save_team_data,
    save_competition_data,
    save_match_data
)

def main():

    # ============================
    # Get FIFA API Data
    # ============================

    match_data = get_match_data()
    team_data = get_team_data()

    # ============================
    # Clean Data
    # ============================

    clean_team_data = prepare_team_data(team_data)
    clean_match_data = prepare_match_data(match_data)
    clean_competition_data = prepare_competition_data(match_data)

    # ============================
    # Database Connection
    # ============================

    connection = connect_database()
    cursor = connection.cursor()

    print("MySQL Connection Success")

    # ============================
    # Save Data
    # ============================

    save_team_data(cursor, clean_team_data)
    save_competition_data(

        cursor,        
        clean_competition_data    
    )

    save_match_data(cursor, clean_match_data)

    # ============================
    # Commit
    # ============================

    connection.commit()

    print("Database Commit Success")

    # ============================
    # Close Database Connection
    # ============================

    cursor.close()
    connection.close()


if __name__ == "__main__":
    main()
