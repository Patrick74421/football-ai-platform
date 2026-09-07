# ============================
# Model Data Imports
# ============================

# Pandas 用來處理與合併模型 DataFrame
import pandas as pd
# 重用 EDA 階段已驗證過的 MySQL Match Data Loader
from analysis.data_loader import load_match_data

# ==== 載入模型原始比賽資料 ====
def load_model_match_data():

    # 從 MySQL 讀取完整 Match DataFrame
    match_df = load_match_data()

    # 將 Match DataFrame 回傳給後續模型資料準備流程
    return match_df

# ==== 將 Match 資料轉成 Team-level Model Data ====
def prepare_team_level_data(match_df):

    # ============================
    # Team A Perspective
    # ============================
    # 從每場比賽中取出：Match ID、日期、Team A、Team B、Team A 進球
    team_a_df = match_df[
        [
            "fifa_match_id",
            "match_date",
            "team_a_fifa_id",
            "team_b_fifa_id",
            "team_a_score"
        ]
    ].copy()

    # 將 Team A 角度的欄位統一改成模型使用名稱
    team_a_df = team_a_df.rename(
        columns={
            "team_a_fifa_id": "team",
            "team_b_fifa_id": "opponent",
            "team_a_score": "goals"
        }
    )

    # ============================
    # Team B Perspective
    # ============================

    # 從同一場比賽中取出：Match ID、日期、Team B、Team A、Team B 進球
    team_b_df = match_df[
        [
            "fifa_match_id",
            "match_date",
            "team_b_fifa_id",
            "team_a_fifa_id",
            "team_b_score"
        ]
    ].copy()

    # 將 Team B 角度的欄位統一改成模型使用名稱
    team_b_df = team_b_df.rename(
        columns={
            "team_b_fifa_id": "team",
            "team_a_fifa_id": "opponent",
            "team_b_score": "goals"
        }
    )

    # ============================
    # Combine Team-level Data
    # ============================

    # 將 Team A 與 Team B 兩個 DataFrame 合併成一份模型資料
    model_df = pd.concat(
        [
            team_a_df,
            team_b_df
        ],
        ignore_index=True
    )

    return model_df

# ==== 依時間切分 Train / Test Data ====
def temporal_train_test_split(model_df, train_ratio=0.8):

    # ============================
    # Prepare Unique Match Order
    # ============================

    # 每場 Match 在 model_df 中有兩筆資料，
    # 因此先只保留 fifa_match_id 與 match_date，
    # 再去除重複 Match，確保切分單位是「比賽」而不是「row」
    match_order_df = model_df[
        [
            "fifa_match_id",
            "match_date"
        ]
    ].drop_duplicates(
        subset=["fifa_match_id"]
    )

    # 將比賽依日期由舊到新排序
    match_order_df = match_order_df.sort_values(
        by=[
            "match_date",
            "fifa_match_id"
        ]
    ).reset_index(
        drop=True
    )
    
    # ============================
    # Decide Split Date
    # ============================

    # 以約 80% 的 Match 作為 Train 區間參考點
    split_index = int(
        len(match_order_df) * train_ratio
    )

    # 取得 Train / Test 的時間分界日期
    split_date = match_order_df.iloc[
        split_index
    ]["match_date"]

    # ============================
    # Split Match IDs
    # ============================

    # 分界日期以前的比賽放入 Train
    train_match_ids = match_order_df[
        match_order_df["match_date"] < split_date
    ]["fifa_match_id"]

    # 分界日期當天以及之後的比賽放入 Test
    test_match_ids = match_order_df[
        match_order_df["match_date"] >= split_date
    ]["fifa_match_id"]

    # ============================
    # Build Train / Test DataFrame
    # ============================

    # 使用 Match ID 將完整 Team-level Data 分成 Train / Test
    train_df = model_df[
        model_df["fifa_match_id"].isin(train_match_ids)
    ].copy()

    # 使用 Test Match ID 建立完整的 Test DataFrame
    test_df = model_df[
        model_df["fifa_match_id"].isin(test_match_ids)
    ].copy()

    # 將 Train / Test 都重新依日期由舊到新排序
    train_df = train_df.sort_values(
        by=[
            "match_date",
            "fifa_match_id"
        ]
    ).reset_index(drop=True)

    test_df = test_df.sort_values(
        by=[
            "match_date",
            "fifa_match_id"
        ]
    ).reset_index(drop=True)

    return train_df, test_df, split_date

# ============================
# Independent Test
# ============================

if __name__ == "__main__":

    # 獨立測試 Model Data Loader 是否可以正常取得 MySQL Match 資料
    match_df = load_model_match_data()

    print("Model Match Data Shape:")
    print(match_df.shape)

    print("Model Match Data Head:")
    print(match_df.head())

    # 將 958 場 Match 轉成 Team-level Model Data
    model_df = prepare_team_level_data(match_df)

    print("Team-level Model Data Shape:")
    print(model_df.shape)

    print("Team-level Model Data Head:")
    print(model_df.head())

    print("Team-level Model Data Tail:")
    print(model_df.tail())

    # 顯示模型資料的最早與最晚比賽日期
    print("Model Data Date Range:")
    print("Earliest Date:", model_df["match_date"].min())
    print("Latest Date:", model_df["match_date"].max())

    # 依照時間建立 Train / Test Data
    train_df, test_df, split_date = temporal_train_test_split(
        model_df
    )

    print("Temporal Split Date:")
    print(split_date)

    print("Train Data Shape:")
    print(train_df.shape)

    print("Test Data Shape:")
    print(test_df.shape)

    print("Train Match Count:")
    print(train_df["fifa_match_id"].nunique())

    print("Test Match Count:")
    print(test_df["fifa_match_id"].nunique())

    print("Train Date Range:")
    print(
        train_df["match_date"].min(),
        "->",
        train_df["match_date"].max()
    )

    print("Test Date Range:")
    print(
        test_df["match_date"].min(),
        "->",
        test_df["match_date"].max()
    )

    # ============================
    # Check Train / Test Match Overlap
    # ============================

    # 將 Train 與 Test 的 Match ID 分別轉成 Python Set
    train_match_id_set = set(
        train_df["fifa_match_id"]
    )

    test_match_id_set = set(
        test_df["fifa_match_id"]
    )

    # 找出同時存在於 Train 與 Test 的 Match ID
    overlap_match_ids = train_match_id_set.intersection(
        test_match_id_set
    )

    print("Train / Test Match Overlap Count:")
    print(len(overlap_match_ids))
