# ============================
# FastAPI Imports
# ============================

# asynccontextmanager 用來管理 FastAPI Application 的啟動與關閉流程
from contextlib import asynccontextmanager

# FastAPI 是建立 Web API Application 的主要 Class
from fastapi import FastAPI, HTTPException

# BaseModel 用來定義與驗證 API 傳入的資料格式
from pydantic import BaseModel

# 使用專案既有的 MySQL Database Connection Function
from backend.database import connect_database

# 初始化 FastAPI 使用的 Production Poisson Model
from models.model_service import( 
    initialize_production_model,
    is_team_supported_by_model,
    predict_matchup_expected_goals,
)

# 計算比分機率矩陣，以及 Team A Win / Draw / Team B Win Probability
from models.prediction import (
    calculate_score_probability_matrix,
    calculate_match_result_probabilities,
)

# ============================
# FastAPI Application
# ============================

# ==== 管理 FastAPI Application 生命週期 ====
@asynccontextmanager
async def lifespan(app: FastAPI):

    # FastAPI Server 啟動時，初始化 Production Poisson Model
    poisson_model, model_df = initialize_production_model()

    # 將模型與 Training Data 儲存在 FastAPI Application State
    # 後續所有 API Request 都可以重複使用，不需要重新訓練模型
    app.state.poisson_model = poisson_model
    app.state.model_df = model_df

    # Application 啟動完成，開始接受 HTTP Request
    yield

    # Application 關閉時清除目前保存的 Model Reference
    app.state.poisson_model = None
    app.state.model_df = None

# 建立 FastAPI Application Instance，並使用自訂 Lifespan
app = FastAPI(lifespan=lifespan)


# 建立 FastAPI Application Instance
#app = FastAPI()

# 建立 FastAPI Application Instance，並使用自訂 Lifespan
app = FastAPI(lifespan=lifespan)

# ============================
# Request Models
# ============================

# 定義 /echo Endpoint 接收的 JSON 資料格式
class EchoRequest(BaseModel):
    team_a_fifa_id: str
    team_b_fifa_id: str

# 定義 /predict Endpoint 接收的 JSON 資料格式
class PredictionRequest(BaseModel):
    team_a_fifa_id: str
    team_b_fifa_id: str

# ==== API Root Endpoint ====
@app.get("/")
def read_root():

    # 回傳 JSON Response
    return {
        "message": "Football AI Platform API"
    }

# ==== API Health Check Endpoint ====
@app.get("/health")
def health_check():

    # 回傳 API Server 目前的基本狀態
    return {
        "status": "ok"
    }

# ==== API Request Body Test Endpoint ====
@app.post("/echo")
def echo_request(data: EchoRequest):

    # 將 Pydantic Model 轉換成 Python Dictionary
    received_data = data.model_dump()

    # 將 Client 傳入的 JSON Data 原樣回傳
    return {
        "received_data": received_data
    }

# ==== 預測單一足球 Matchup ====
@app.post("/predict")
def predict_match(data: PredictionRequest):

    # 從 FastAPI Application State 取得已經訓練完成的 Production Model
    poisson_model = app.state.poisson_model

    # 從 FastAPI Application State 取得 Model Training Data
    model_df = app.state.model_df

    # Team A 與 Team B 必須是不同球隊
    if data.team_a_fifa_id == data.team_b_fifa_id:
        raise HTTPException(
            status_code=400,
            detail="Team A and Team B must be different teams"
        )

    # 檢查 Team A 是否存在於 Production Model Training Data
    team_a_supported = is_team_supported_by_model(
        model_df,
        data.team_a_fifa_id
    )

    # 如果 Team A 不被目前模型支援，停止 Prediction
    if not team_a_supported:
        raise HTTPException(
            status_code=400,
            detail=f"Team A ID '{data.team_a_fifa_id}' is not supported by the current model"
        )

    # 檢查 Team B 是否存在於 Production Model Training Data
    team_b_supported = is_team_supported_by_model(
        model_df,
        data.team_b_fifa_id
    )

    # 如果 Team B 不被目前模型支援，停止 Prediction
    if not team_b_supported:
        raise HTTPException(
            status_code=400,
            detail=f"Team B ID '{data.team_b_fifa_id}' is not supported by the current model"
        )

    # 使用 Team A 與 Team B 計算 Expected Goals
    lambda_a, lambda_b = predict_matchup_expected_goals(
         poisson_model,
         data.team_a_fifa_id,
         data.team_b_fifa_id
    )
    
    # 使用兩支球隊的 Expected Goals 建立 0~10 球 Score Probability Matrix
    score_matrix = calculate_score_probability_matrix(
        lambda_a,
        lambda_b,
        max_goals=10
    )

    # 將所有比分機率整理成 Team A Win / Draw / Team B Win Probability
    (
        team_a_win_probability,
        draw_probability,
        team_b_win_probability
    ) = calculate_match_result_probabilities(
        score_matrix
    )
    
    # 回傳兩支球隊 ID 與 Expected Goals
    return {
        "team_a_fifa_id": data.team_a_fifa_id,
        "team_b_fifa_id": data.team_b_fifa_id,
        "lambda_a": lambda_a,
        "lambda_b": lambda_b,
        "team_a_win_probability": team_a_win_probability,
        "draw_probability": draw_probability,
        "team_b_win_probability": team_b_win_probability
    }


# ==== 取得單一球隊資料 ====
@app.get("/teams/{team_id}")
def get_team(team_id: str):

    # 建立 MySQL Database Connection
    connection = connect_database()

    # 建立 Dictionary Cursor
    # 查詢結果會以 Python Dictionary 的形式回傳
    cursor = connection.cursor(dictionary=True)

    # 使用 fifa_team_id 查詢指定球隊
    query = """
        SELECT
            fifa_team_id,
            association_id,
            team_name,
            confederation_id,
            confederation_name
        FROM team
        WHERE fifa_team_id = %s
    """

    # 使用 Parameterized Query 執行 SQL
    cursor.execute(query, (team_id,))

    # 取得符合條件的一筆 Team 資料
    team_result = cursor.fetchone()

    # 使用完成後關閉 Cursor
    cursor.close()

    # 使用完成後關閉 Database Connection
    connection.close()

    # 如果 MySQL 找不到指定 Team，回傳 HTTP 404
    if team_result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Team ID '{team_id}' not found"
        )

    # 回傳 Team 查詢結果
    return team_result

# ==== 取得單一比賽資料 ====
@app.get("/matches/{match_id}")
def get_match(match_id: str):

    # 建立 MySQL Database Connection
    connection = connect_database()

    # 建立 Dictionary Cursor
    # 查詢結果會以 Python Dictionary 的形式回傳
    cursor = connection.cursor(dictionary=True)

    # 使用 fifa_match_id 查詢指定比賽
    query = """
        SELECT
            fifa_match_id,
            match_date,
            fifa_competition_id,
            team_a_fifa_id,
            team_b_fifa_id,
            team_a_score,
            team_b_score
        FROM matches
        WHERE fifa_match_id = %s
    """

    # 使用 Parameterized Query 執行 SQL
    cursor.execute(query, (match_id,))

    # 取得符合條件的一筆 Match 資料
    match_result = cursor.fetchone()

    # 使用完成後關閉 Cursor
    cursor.close()

    # 使用完成後關閉 Database Connection
    connection.close()

    # 如果 MySQL 找不到指定 Match，回傳 HTTP 404
    if match_result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Match ID '{match_id}' not found"
        )

    # 回傳 Match 查詢結果
    return match_result

# ==== 檢查 MySQL Database 連線 ====
@app.get("/database-health")
def database_health():

    # 使用專案既有 Function 建立 MySQL Connection
    connection = connect_database()

    # 建立 Cursor，讓 Python 可以送 SQL 給 MySQL
    cursor = connection.cursor()

    # 執行最簡單的 SQL，確認 Database 可以正常執行查詢
    cursor.execute("SELECT 1")

    # 取得 SQL 查詢結果
    result = cursor.fetchone()

    # 使用完成後關閉 Cursor
    cursor.close()

    # 使用完成後關閉 Database Connection
    connection.close()

    # 回傳 Database 連線測試結果
    return { "database": "ok", "result": result[0] }
