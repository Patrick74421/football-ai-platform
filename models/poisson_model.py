# ============================
# Poisson Model Imports
# ============================

# NumPy 用來檢查模型參數是否為有限數值
import numpy as np

# statsmodels.api 提供 GLM 使用的 Poisson probability family
import statsmodels.api as sm

# statsmodels.formula.api 提供公式形式的 GLM 建模介面
import statsmodels.formula.api as smf

# 重用模型資料準備流程
from models.data_preparation import (
    load_model_match_data,
    prepare_team_level_data,
    temporal_train_test_split
)

# ==== 檢查 Poisson Training Data 狀況 ====
def inspect_poisson_training_data(train_df):

    # ============================
    # Team Statistics
    # ============================

    # 依 team 分組，計算每支球隊：
    # count = 有多少筆訓練資料
    # sum   = 總共進多少球
    team_stats = train_df.groupby(
        "team"
    )["goals"].agg(
        [
            "count",
            "sum"
        ]
    )

    # 找出 Train 中完全沒有進球的球隊
    zero_goal_teams = team_stats[
        team_stats["sum"] == 0
    ]

    # ============================
    # Opponent Statistics
    # ============================

    # 依 opponent 分組，
    # 查看每支球隊作為對手時有多少資料，以及對手總共進多少球
    opponent_stats = train_df.groupby(
        "opponent"
    )["goals"].agg(
        [
            "count",
            "sum"
        ]
    )

    # 找出作為 opponent 時，
    # 歷史資料中對手完全沒有進球的球隊
    zero_goal_opponents = opponent_stats[
        opponent_stats["sum"] == 0
    ]

    print("Unique Teams in Train:")
    print(train_df["team"].nunique())

    print("Minimum Team Observations:")
    print(team_stats["count"].min())

    print("Teams With Only 1 Observation:")
    print(
        (team_stats["count"] == 1).sum()
    )

    print("Teams With Zero Total Goals:")
    print(len(zero_goal_teams))

    print("Zero-goal Teams:")
    print(zero_goal_teams)

    print("Minimum Opponent Observations:")
    print(opponent_stats["count"].min())

    print("Opponents With Only 1 Observation:")
    print(
        (opponent_stats["count"] == 1).sum()
    )

    print("Opponents With Zero Goals Allowed:")
    print(len(zero_goal_opponents))

    print("Zero-goal Opponents:")
    print(zero_goal_opponents)

# ==== 訓練 Poisson Regression Model ====
def train_poisson_model(train_df):

    # 建立 Generalized Linear Model（廣義線性模型）
    # goals 為預測目標
    # team 與 opponent 都視為 categorical feature（類別特徵）
    poisson_model = smf.glm(
        formula="goals ~ C(team) + C(opponent)",
        data=train_df,
        family=sm.families.Poisson()
    ).fit()

    return poisson_model

# ==== 訓練加入 L2 Regularization 的 Poisson Regression ====
def train_regularized_poisson_model(train_df, alpha=0.1):

    # 建立與原本相同的 Poisson GLM：
    # goals 為預測目標，
    # team 與 opponent 為 categorical feature
    poisson_glm = smf.glm(
        formula="goals ~ C(team) + C(opponent)",
        data=train_df,
        family=sm.families.Poisson()
    )

    # 使用 L2 Regularization 訓練模型，
    # 避免 sparse categorical data 讓 coefficient 過度極端
    regularized_model = poisson_glm.fit_regularized(
        alpha=alpha,
        L1_wt=0.0
    )

    return regularized_model

# ==== 檢查 Test 是否包含 Train 未出現的球隊 ====
def inspect_unseen_categories(train_df, test_df):

    # 將 Train 中出現過的 team 轉成 Python Set
    train_teams = set( train_df["team"] )

    # 將 Test 中出現的 team 轉成 Python Set
    test_teams = set( test_df["team"] )

    # 找出 Test 有、但 Train 沒有的 team
    unseen_teams = test_teams.difference( train_teams )

    # 將 Train 中出現過的 opponent 轉成 Python Set
    train_opponents = set( train_df["opponent"] )

    # 將 Test 中出現的 opponent 轉成 Python Set
    test_opponents = set( test_df["opponent"] )

    # 找出 Test 有、但 Train 沒有的 opponent
    unseen_opponents = test_opponents.difference( train_opponents )

    print("Unseen Teams in Test:")
    print(unseen_teams)

    print("Unseen Team Count:")
    print(len(unseen_teams))

    print("Unseen Opponents in Test:")
    print(unseen_opponents)

    print("Unseen Opponent Count:")
    print(len(unseen_opponents))

    # ============================
    # Check Affected Test Matches
    # ============================

    # 找出 Test 中，只要 team 或 opponent 包含 unseen category 的資料
    affected_test_df = test_df[
        test_df["team"].isin(unseen_teams)
        |
        test_df["opponent"].isin(unseen_opponents)
    ].copy()

    # 顯示受 unseen category 影響的 Team-level row 數量
    print("Affected Test Rows:")
    print(len(affected_test_df))

    # 顯示受 unseen category 影響的實際 Match 數量
    print("Affected Test Match Count:")
    print(
        affected_test_df["fifa_match_id"].nunique()
    )

# ==== 將 Test 分成可預測資料與 Cold Start 資料 ====
def split_seen_and_cold_start_test_data(train_df, test_df):
    
    # 將 Train 中模型看過的 team 與 opponent 儲存成 Python Set
    train_teams = set( train_df["team"] )
    train_opponents = set( train_df["opponent"] )

    # ============================
    # Find Cold Start Rows
    # ============================

    # 找出 team 或 opponent 沒有出現在 Train 的 Test rows
    cold_start_rows = test_df[
        (~test_df["team"].isin(train_teams))
        |
        (~test_df["opponent"].isin(train_opponents))
    ]

    # 取得受 Cold Start 影響的完整 Match ID
    cold_start_match_ids = set( cold_start_rows["fifa_match_id"] )

    # ============================
    # Build Seen Test Data
    # ============================

    # 排除 Cold Start Match，
    # 只保留模型已看過所有 categorical values 的比賽
    seen_test_df = test_df[
        ~test_df["fifa_match_id"].isin(
            cold_start_match_ids
        )
    ].copy()

    # ============================
    # Build Cold Start Test Data
    # ============================

    # Cold Start Match 不刪除，
    # 獨立保留供之後設計 fallback strategy
    cold_start_test_df = test_df[
        test_df["fifa_match_id"].isin(
            cold_start_match_ids
        )
    ].copy()

    return seen_test_df, cold_start_test_df

# ==== 使用 Poisson Model 預測 Expected Goals Lambda ====
def predict_expected_goals(poisson_model, prediction_df):

    # 複製 Prediction DataFrame，
    # 避免直接修改原本的 Test Data
    prediction_result_df = prediction_df.copy()

    # 使用已訓練完成的 Poisson Regression，
    # 根據 team 與 opponent 預測每一筆資料的 lambda
    prediction_result_df["lambda"] = poisson_model.predict(
        prediction_result_df
    )

    return prediction_result_df

# ============================
# Independent Test
# ============================

if __name__ == "__main__":

    # 從 MySQL 取得原始 Match Data
    match_df = load_model_match_data()

    # 將 958 場 Match 轉為 1916 筆 Team-level Data
    model_df = prepare_team_level_data(
        match_df
    )

    # 使用時間順序建立 Train / Test Data
    train_df, test_df, split_date = temporal_train_test_split(
        model_df
    )

    print("Train Data Shape:")
    print(train_df.shape)

    print("Test Data Shape:")
    print(test_df.shape)

    # 在正式訓練前檢查 categorical data 是否過度稀疏
    inspect_poisson_training_data( train_df )

    # 檢查 Test 是否包含 Train 未出現的 categorical value
    inspect_unseen_categories( train_df, test_df )

    # 將 Test 分成正常可預測資料與 Cold Start 資料
    seen_test_df, cold_start_test_df = split_seen_and_cold_start_test_data( train_df, test_df )

    print("Seen Test Data Shape:")
    print(seen_test_df.shape)

    print("Seen Test Match Count:")
    print( seen_test_df["fifa_match_id"].nunique() )

    print("Cold Start Test Data Shape:")
    print(cold_start_test_df.shape)

    print("Cold Start Test Match Count:")
    print( cold_start_test_df["fifa_match_id"].nunique() )

    # 使用 L2 Regularization 訓練 Poisson Regression
    regularized_model = train_regularized_poisson_model( train_df, alpha=0.1 )

    
    print("Regularized Poisson Model Training Success")

    # Train Data 實際使用的資料筆數
    print("Number of Training Observations:")
    print(len(train_df))

    # 檢查所有模型 coefficient 是否都是有限數值，
    # 避免再次出現 NaN 或 inf
    print("All Model Parameters Finite:")
    print(
        np.isfinite(
            regularized_model.params
        ).all()
    )

    # 顯示模型實際估計了多少個 coefficient
    print("Number of Model Parameters:")
    print( len(regularized_model.params) )

    # 訓練 Poisson Regression
    #poisson_model = train_poisson_model( train_df )

    #print("Poisson Model Training Success")

    # 顯示模型實際使用的訓練資料筆數
    #print("Number of Training Observations:")
    #print(poisson_model.nobs)

    # 顯示模型是否成功收斂
    #print("Model Converged:")
    #print(poisson_model.converged)

    # 使用 Seen Test Data 預測每支球隊的 Expected Goals Lambda
    prediction_result_df = predict_expected_goals( regularized_model, seen_test_df )

    print("Prediction Result Shape:")
    print(prediction_result_df.shape)

    print("Prediction Result Head:")
    print( prediction_result_df[
        [ "fifa_match_id", "team", "opponent", "goals", "lambda" ]
        ].head()
    )

    print("Lambda Minimum:")
    print( prediction_result_df["lambda"].min() )

    print("Lambda Maximum:")
    print( prediction_result_df["lambda"].max() )

    print("Lambda Average:")
    print( prediction_result_df["lambda"].mean() )

    print("All Lambda Values Finite:")
    print( np.isfinite(
        prediction_result_df["lambda"]
        ).all()
    )

    print("All Lambda Values Positive:")
    print(
        ( prediction_result_df["lambda"] > 0 ).all()
    )
