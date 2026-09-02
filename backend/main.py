# ============================
# Backend Module Imports
# ============================

# 從 FIFA Crawler 模組匯入 API 資料取得函式

from backend.fifa_crawler import get_match_data, get_team_data


# 從 Data Cleaner 模組匯入資料清理函式
from backend.data_cleaner import (
    prepare_team_data,
    prepare_match_data,
    prepare_competition_data
)

# 從 Database 模組匯入 MySQL 連線與資料寫入函式
from backend.database import (
    connect_database,
    save_team_data,
    save_competition_data,
    save_match_data
)

# ============================
# Main Data Pipeline
# ============================

def main():

    # 先設定成 None，避免資料庫連線建立失敗時，finally 區塊找不到這兩個變數
    connection = None
    cursor = None

    try:

        # ============================
        # Get FIFA API Data
        # ============================

        # 從 FIFA API 取得原始 Match / Team 資料
        match_data = get_match_data()
        team_data = get_team_data()

        # ============================
        # Clean Data
        # ============================

        # 將 API 原始資料轉成專案統一使用的乾淨格式
        clean_team_data = prepare_team_data(team_data)
        clean_match_data = prepare_match_data(match_data)
        clean_competition_data = prepare_competition_data(match_data)

        # ============================
        # Database Connection
        # ============================

        # 建立 MySQL Connection 與 Cursor
        connection = connect_database()
        cursor = connection.cursor()

        print("MySQL Connection Success")

        # ============================
        # Save Data
        # ============================

        # 先寫 Team，因為 matches.team_a_fifa_id / team_b_fifa_id
        # Foreign Key 會參考 team table
        save_team_data( cursor, clean_team_data )

        # 再寫 Competition，因為 matches.fifa_competition_id
        # Foreign Key 會參考 competition table
        save_competition_data( cursor, clean_competition_data )

        # Team / Competition 都存在後，最後才寫入 Match
        save_match_data( cursor,clean_match_data )

        # ============================
        # Commit Transaction
        # ============================

        # 前面全部 INSERT / UPDATE 成功後，才正式提交這次 Transaction
        connection.commit()

        print("Database Commit Success")

    except Exception as error:

        # ============================
        # Rollback Transaction
        # ============================

        # ============================
        # 如果 Database Connection 已經建立，且後面的資料處理發生錯誤，
        # 就取消本次尚未 commit 的資料變更
        if connection is not None:

            connection.rollback()
            print("Database Rollback")

        # 顯示實際錯誤內容，方便 Debug
        print("Pipeline Error:")
        print(error)

        # 將 Exception 繼續往外拋，保留完整 Traceback，方便找出錯誤位置
        raise

    finally:
        # ============================
        # Close Database Resources
        # ============================

        # finally 不論 try 成功或 except 發生，最後都一定會執行

        # Cursor 有成功建立才關閉
        if cursor is not None:

            cursor.close()
            print("MySQL Cursor Closed")

        # Connection 有成功建立才關閉
        if connection is not None:

            connection.close()
            print("MySQL Connection Closed")


if __name__ == "__main__":
    main()
