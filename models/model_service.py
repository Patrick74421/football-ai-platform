# ============================
# Model Service Imports
# ============================

# Pandas 用來建立模型 Prediction 所需要的 DataFrame
import pandas as pd

# 載入 MySQL Match Data，並轉換成模型使用的 Team-level Data
from models.data_preparation import (
    load_model_match_data,
    prepare_team_level_data,
)

# 使用 Regularized Poisson Regression 訓練模型
from models.poisson_model import (
    train_regularized_poisson_model,
    predict_expected_goals,
)

# ==== 初始化 Production Poisson Model ====
def initialize_production_model():

    # 從 MySQL 載入目前所有歷史比賽資料
    match_df = load_model_match_data()

    # 將 Match-level Data 轉換成 Poisson Model 使用的 Team-level Data
    model_df = prepare_team_level_data( match_df )

    # 使用全部 Historical Data 訓練 Production Poisson Model
    poisson_model = train_regularized_poisson_model( model_df, alpha=0.1 )

    
    # 回傳訓練完成的模型，以及模型使用的歷史資料
    return poisson_model, model_df

# ==== 檢查 Team 是否存在於 Production Model Training Data ====
def is_team_supported_by_model(model_df, team_id):

    # 取得 Training Data 中所有出現過的 Team ID
    trained_team_ids = set(model_df["team"])

    # 判斷指定 Team ID 是否存在於模型的 Training Data
    return team_id in trained_team_ids

# ==== 預測單一 Matchup 的 Expected Goals ====
def predict_matchup_expected_goals( poisson_model, team_a_id, team_b_id ):

    # 建立兩筆 Prediction Data
    # 第一筆：Team A 對 Team B
    # 第二筆：Team B 對 Team A
    prediction_df = pd.DataFrame([
        {
            "team": team_a_id,
            "opponent": team_b_id
        },
        {
            "team": team_b_id,
            "opponent": team_a_id
        }
    ])

    # 使用已訓練完成的 Poisson Model 計算 Expected Goals
    prediction_result_df = predict_expected_goals(
        poisson_model,
        prediction_df
    )

    # 第一筆資料是 Team A 的 Expected Goals
    lambda_a = float(
        prediction_result_df.iloc[0]["lambda"]
    )

    # 第二筆資料是 Team B 的 Expected Goals
    lambda_b = float(
        prediction_result_df.iloc[1]["lambda"]
    )

    # 回傳 Team A 與 Team B 的 Expected Goals
    return lambda_a, lambda_b
