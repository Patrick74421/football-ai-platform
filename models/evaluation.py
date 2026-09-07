# ============================
# Evaluation Imports
# ============================

# 載入模型資料準備相關 Function
from models.data_preparation import (
    load_model_match_data,
    prepare_team_level_data,
    temporal_train_test_split
)

# 載入 Poisson Model 訓練與 Lambda Prediction Function
from models.poisson_model import (
    train_regularized_poisson_model,
    split_seen_and_cold_start_test_data,
    predict_expected_goals
)

# 載入 Score Matrix 與 W / D / L Probability Function
from models.prediction import (
    calculate_score_probability_matrix,
    calculate_match_result_probabilities
)


# ============================
# Model Evaluation
# ============================

# ==== 計算 Goals Prediction MAE ====
def calculate_goal_mae(prediction_result_df):

    # 計算每一筆：
    # 實際 goals 與模型預測 lambda 之間的絕對誤差
    absolute_errors = (
        prediction_result_df["goals"] - prediction_result_df["lambda"]
    ).abs()

    # 將所有絕對誤差取平均
    mae = absolute_errors.mean()

    return mae

# ==== 建立 Match-level Prediction Data ====
def prepare_match_level_prediction_data( match_df, prediction_result_df ):

    # ============================
    # Prepare Seen Match Data
    # ============================

    # 取得目前真正有 Lambda Prediction 的 Match ID
    prediction_match_ids = ( prediction_result_df["fifa_match_id"].unique() )

    # 從原始 Match Data 中，
    # 只保留這次 Seen Test 裡可以評估的比賽
    match_prediction_df = match_df[
        match_df["fifa_match_id"].isin( prediction_match_ids )
    ].copy()

    # ============================
    # Prepare Team A Lambda
    # ============================

    # 取出每支 Team 的 Lambda，
    # 並改名成 Team A Merge 所需要的欄位名稱
    team_a_lambda_df = prediction_result_df[
        [
            "fifa_match_id",
            "team",
            "lambda"
        ]
    ].rename( columns={
        "team": "team_a_fifa_id",
        "lambda": "lambda_a"
        }
    )

    # 將 Team A 的 Lambda 接回原始 Match Data
    match_prediction_df = match_prediction_df.merge(     
        team_a_lambda_df,
        on=[
            "fifa_match_id",
            "team_a_fifa_id"                
        ],
        how="inner"

    )

    # ============================
    # Prepare Team B Lambda
    # ============================

    # 使用同一批 Prediction，
    # 改名成 Team B Merge 所需要的欄位名稱
    team_b_lambda_df = prediction_result_df[
        [
            "fifa_match_id",
            "team",
            "lambda"
        ]
    ].rename(
        columns={
            "team": "team_b_fifa_id",
            "lambda": "lambda_b"
        }
    )

    # 將 Team B 的 Lambda 接回同一場 Match
    match_prediction_df = match_prediction_df.merge(
        team_b_lambda_df,
        on=[
            "fifa_match_id",
            "team_b_fifa_id"
        ],
        how="inner"
    )

    return match_prediction_df

# ==== 計算每場比賽的 Win / Draw / Loss Probability ====
def calculate_match_result_prediction_probabilities( match_prediction_df, max_goals=10 ):

    # 複製 Match-level Data，
    # 避免直接修改原始 DataFrame
    result_df = match_prediction_df.copy()

    # 分別儲存每場比賽的三種結果機率
    team_a_win_probabilities = []
    draw_probabilities = []
    team_b_win_probabilities = []
    
    # 一場一場讀取 Match-level Prediction Data
    for _, match in result_df.iterrows():

        # 使用目前這場比賽的 lambda_a 與 lambda_b，
        # 建立 Score Probability Matrix
        score_matrix = calculate_score_probability_matrix(
            match["lambda_a"],
            match["lambda_b"],
            max_goals
        )

        # 將 Score Matrix 分成 Team A Win、Draw、Team B Win
        (
            team_a_win_probability,
            draw_probability,
            team_b_win_probability
        ) = calculate_match_result_probabilities(
            score_matrix
        )

        # 儲存目前這場比賽的三種結果機率
        team_a_win_probabilities.append( team_a_win_probability )

        draw_probabilities.append( draw_probability )

        team_b_win_probabilities.append( team_b_win_probability )

    # 將 215 場比賽的三種結果機率加入 DataFrame
    result_df["team_a_win_probability"] = ( team_a_win_probabilities )

    result_df["draw_probability"] = ( draw_probabilities )

    result_df["team_b_win_probability"] = ( team_b_win_probabilities ) 

    return result_df

# ==== 建立每場比賽的實際結果 ====
def add_actual_match_result(match_result_prediction_df):

    # 複製資料，
    # 避免直接修改原始 Match Result Prediction DataFrame
    result_df = match_result_prediction_df.copy()

    # 儲存每場比賽的實際結果
    actual_results = []

    # 一場一場讀取 Match-level Data
    for _, match in result_df.iterrows():

        # Team A 實際進球較多 → Team A Win
        if match["team_a_score"] > match["team_b_score"]:

            actual_result = "Team A Win"

        # 兩隊實際進球相同 → Draw
        elif match["team_a_score"] == match["team_b_score"]:

            actual_result = "Draw"

        # Team B 實際進球較多 → Team B Win
        else:

            actual_result = "Team B Win"

        # 儲存目前這場比賽的實際結果
        actual_results.append( actual_result )

    # 將 215 場比賽的實際結果加入 DataFrame
    result_df["actual_result"] = actual_results

    return result_df

# ==== 建立每場比賽的模型預測結果 ====
def add_predicted_match_result(match_result_df):

    # 複製資料，
    # 避免直接修改原始 Match Result DataFrame
    result_df = match_result_df.copy()

    # 儲存每場比賽的模型預測結果
    predicted_results = []

    # 一場一場讀取 Match-level Data
    for _, match in result_df.iterrows():

        # 找出 Team A Win、Draw、Team B Win
        # 三種結果機率中的最大值
        max_probability = max(
            match["team_a_win_probability"],
            match["draw_probability"],
            match["team_b_win_probability"]
        )

        # Team A Win Probability 最大
        if max_probability == match["team_a_win_probability"]:

            predicted_result = "Team A Win"

        # Draw Probability 最大
        elif max_probability == match["draw_probability"]:
            
            predicted_result = "Draw"

        # Team B Win Probability 最大
        else:

            predicted_result = "Team B Win"

        # 儲存目前這場比賽的模型預測結果
        predicted_results.append( predicted_result )

    # 將 215 場比賽的模型預測結果加入 DataFrame
    result_df["predicted_result"] = predicted_results

    return result_df

# ==== 判斷每場比賽的模型預測是否正確 ====
def add_prediction_correctness(evaluation_result_df):

    # 複製資料，
    # 避免直接修改原始 Evaluation DataFrame
    result_df = evaluation_result_df.copy()

    # 逐筆比較 Actual Result 與 Predicted Result，
    # 相同為 True，不同為 False
    result_df["is_correct"] = (
        result_df["actual_result"] == result_df["predicted_result"]
    )

    return result_df

# ==== 計算 Match Result Prediction Accuracy ====
def calculate_match_result_accuracy(evaluation_result_df):

    # 計算 is_correct 中 True 的比例，
    # True 會視為 1，False 會視為 0
    accuracy = evaluation_result_df["is_correct"].mean()

    return accuracy

# ==== 統計 Actual / Predicted Match Result 分布 ====
def calculate_match_result_distribution(evaluation_result_df):

    # 統計實際 Team A Win、Draw、Team B Win 各有幾場
    actual_result_distribution = (
        evaluation_result_df["actual_result"].value_counts()
    )

    # 統計模型預測 Team A Win、Draw、Team B Win 各有幾場
    predicted_result_distribution = (
        evaluation_result_df["predicted_result"].value_counts()
    )

    return ( actual_result_distribution, predicted_result_distribution )

# ==== 計算 Majority Class Baseline Accuracy ====
def calculate_majority_baseline_accuracy( match_df, train_df, evaluation_result_df ):

    # ============================
    # Prepare Train Match Data
    # ============================

    # 取得 Train Data 中不重複的 Match ID
    train_match_ids = train_df["fifa_match_id"].unique()

    # 從原始 Match Data 中，
    # 只保留屬於 Training Data 的比賽
    train_match_df = match_df[
        match_df["fifa_match_id"].isin( train_match_ids )
    ].copy()

    # 根據 Training Match 的實際比分，
    # 建立 Team A Win / Draw / Team B Win
    train_match_df = add_actual_match_result( train_match_df )
    
    # ============================
    # Find Majority Class
    # ============================

    # 統計 Training Data 中三種比賽結果的出現次數
    train_result_counts = ( train_match_df["actual_result"].value_counts() )

    # 找出 Training Data 中出現次數最多的結果
    baseline_result = train_result_counts.idxmax()

    # ============================
    # Calculate Baseline Accuracy
    # ============================

    # Baseline 永遠預測 Training Data 中最常見的結果，
    # 再與 Test Data 的 Actual Result 比較
    baseline_accuracy = (
        evaluation_result_df["actual_result"] == baseline_result
    ).mean()

    return baseline_result, baseline_accuracy

# ==== 比較 Model Accuracy 與 Baseline Accuracy ====
def compare_model_and_baseline_accuracy( model_accuracy, baseline_accuracy ):

    # 計算 Model Accuracy 相對於 Baseline Accuracy 的差距
    accuracy_difference = (
        model_accuracy - baseline_accuracy
    )

    return accuracy_difference


# ============================
# Independent Test
# ============================

if __name__ == "__main__":

    # 從 MySQL 載入原始比賽資料
    match_df = load_model_match_data()

    # 將每場比賽轉換成 Team-level Model Data
    model_df = prepare_team_level_data( match_df )

    # 按照時間順序切分 Train / Test
    # 同時取得 Train / Test 的時間分界日期
    train_df, test_df, split_date = temporal_train_test_split( model_df )

    # 使用 Train Data 訓練 Regularized Poisson Model
    poisson_model = train_regularized_poisson_model( train_df )

    # 將 Test Data 分成可預測資料與 Cold Start 資料
    seen_test_df, cold_start_test_df = (
        split_seen_and_cold_start_test_data( train_df, test_df )
    )

    # 使用模型對 Seen Test Data 預測 Lambda
    prediction_result_df = predict_expected_goals( poisson_model, seen_test_df )

    # 確認 Evaluation 已取得真正的 Prediction Data
    print("Evaluation Prediction Shape:")
    print( prediction_result_df.shape )

    print("Evaluation Prediction Head:")
    print( prediction_result_df.head() )

    # ============================
    # Calculate Goal MAE
    # ============================

    # 使用 430 筆 Seen Test Prediction，
    # 計算實際 goals 與預測 lambda 的平均絕對誤差
    goal_mae = calculate_goal_mae( prediction_result_df )

    print("Goal Prediction MAE:")
    print( goal_mae )

    # ============================
    # Prepare Match-level Prediction Data
    # ============================

    # 將 Team-level Lambda Prediction，
    # 依照原始 Team A / Team B 身分整理回一場 Match 一列
    match_prediction_df = prepare_match_level_prediction_data(
        match_df,
        prediction_result_df
    )

    # 確認 Match-level Prediction Data 的資料筆數
    print("Match-level Prediction Shape:")
    print( match_prediction_df.shape )

    # 查看 Team A / Team B 與各自 Lambda
    print("Match-level Prediction Head:")
    print(
        match_prediction_df[
            [
                "fifa_match_id",
                "team_a_fifa_id",
                "team_b_fifa_id",
                "team_a_score",
                "team_b_score",
                "lambda_a",
                "lambda_b"
            ]
        ].head()
    )

    # ============================
    # Calculate Match Result Probabilities
    # ============================

    # 將 215 場 Match 的 lambda_a / lambda_b，
    # 轉換成 Team A Win、Draw、Team B Win 機率
    match_result_prediction_df = (
        calculate_match_result_prediction_probabilities( match_prediction_df )
    )

    # 確認 215 場比賽都成功建立三種結果機率
    print("Match Result Prediction Shape:")
    print( match_result_prediction_df.shape )

    # 查看前 5 場比賽的預測結果
    print("Match Result Prediction Head:")
    print(
        match_result_prediction_df[
            [
                "fifa_match_id",
                "lambda_a",
                "lambda_b",
                "team_a_win_probability",
                "draw_probability",
                "team_b_win_probability"
            ]
        ].head()
    )

    # ============================
    # Add Actual Match Result
    # ============================

    # 根據實際 Team A / Team B Score，
    # 建立每場比賽真正的 Actual Result
    actual_result_df = add_actual_match_result( match_result_prediction_df )

    # ============================
    # Add Predicted Match Result
    # ============================

    # 根據三種預測機率中的最大值，
    # 建立模型的 Predicted Result
    evaluation_result_df = add_predicted_match_result( actual_result_df )

    # 確認 Actual Result 與 Predicted Result
    # 都已成功加入 Match-level Data
    print("Actual / Predicted Result Shape:")
    print( evaluation_result_df.shape )

    print("Actual / Predicted Result Head:")
    print(
        evaluation_result_df[
            [
                "fifa_match_id",
                "team_a_score",
                "team_b_score",
                "team_a_win_probability",
                "draw_probability",
                "team_b_win_probability",
                "actual_result",
                "predicted_result"
            ]
        ].head()
    )

    # ============================
    # Add Prediction Correctness
    # ============================

    # 比較 Actual Result 與 Predicted Result，
    # 為每一場比賽建立 True / False
    evaluation_result_df = add_prediction_correctness( evaluation_result_df )

    # 確認 is_correct 欄位已成功加入
    print("Prediction Correctness Shape:")
    print( evaluation_result_df.shape )

    print("Prediction Correctness Head:")
    print(
        evaluation_result_df[
            [
                "fifa_match_id",
                "actual_result",
                "predicted_result",
                "is_correct"
            ]
        ].head()
    )

    # ============================
    # Calculate Match Result Accuracy
    # ============================

    # 計算 215 場 Test Match 的勝平負預測正確率
    match_result_accuracy = calculate_match_result_accuracy( evaluation_result_df )

    print("Match Result Accuracy:")
    print( match_result_accuracy )

    # ============================
    # Calculate Match Result Distribution
    # ============================

    # 統計 215 場 Test Match 的
    # Actual Result 與 Predicted Result 分布
    (
        actual_result_distribution,
        predicted_result_distribution
    ) = calculate_match_result_distribution(
        evaluation_result_df
    )

    print("Actual Result Distribution:")
    print( actual_result_distribution )

    print("Predicted Result Distribution:")
    print( predicted_result_distribution )

    # ============================
    # Calculate Majority Baseline Accuracy
    # ============================

    # 使用 Training Data 找出最常見的比賽結果，
    # 並用這個固定結果評估 215 場 Seen Test Match
    baseline_result, baseline_accuracy = (
        calculate_majority_baseline_accuracy(
            match_df,
            train_df,
            evaluation_result_df
        )
    )

    print("Majority Baseline Result:")
    print( baseline_result )

    print("Majority Baseline Accuracy:")
    print( baseline_accuracy )

    # ============================
    # Compare Model and Baseline Accuracy
    # ============================

    # 計算 Poisson Model Accuracy
    # 與 Majority Baseline Accuracy 的差距
    accuracy_difference = compare_model_and_baseline_accuracy(
        match_result_accuracy,
        baseline_accuracy
    )

    print("Model vs Baseline Accuracy Difference:")
    print( accuracy_difference )
