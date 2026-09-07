# ============================
# Prediction Imports
# ============================

# math 提供 exponential 與 factorial 等數學運算
import math

# ==== 計算單一球隊的 Poisson 進球機率 ====
def calculate_goal_probabilities(lambda_value, max_goals=10):

    # 儲存 0 球 ~ max_goals 球的機率
    goal_probabilities = []

    # 依序計算 0 球、1 球、2 球 ... max_goals 球
    for goals in range(max_goals + 1):

        # Poisson Probability Mass Function:
        # P(X = k) = e^(-lambda) * lambda^k / k!
        probability = (
            math.exp(-lambda_value)
            * (lambda_value ** goals)
            / math.factorial(goals)
        )

        # 將目前進球數的機率加入 List
        goal_probabilities.append(probability)

    return goal_probabilities

# ==== 計算一場比賽兩支球隊的 Poisson 進球機率 ====
def calculate_match_goal_probabilities( lambda_a, lambda_b, max_goals=10 ):

    # 使用 Team A 的 lambda，
    # 計算 Team A 進 0 ~ max_goals 球的機率
    team_a_probabilities = calculate_goal_probabilities( lambda_a, max_goals )

    # 使用 Team B 的 lambda，
    # 計算 Team B 進 0 ~ max_goals 球的機率
    team_b_probabilities = calculate_goal_probabilities( lambda_b, max_goals )

    return team_a_probabilities, team_b_probabilities

# ==== 建立比分機率矩陣 ====
def calculate_score_probability_matrix( lambda_a, lambda_b, max_goals=10 ):

    # 先分別計算 Team A 與 Team B 的 0 ~ max_goals 進球機率
    team_a_probabilities, team_b_probabilities = (
         calculate_match_goal_probabilities( lambda_a, lambda_b, max_goals )
     )
    
    # 建立空的 Score Probability Matrix
    score_matrix = []

    # 每一個 row 代表 Team A 的進球數
    for team_a_goals in range(max_goals + 1):

        # 儲存目前 Team A 進球數下，
        # Team B 各種進球數所對應的比分機率
        score_row = []

        # 每一個 column 代表 Team B 的進球數
        for team_b_goals in range(max_goals + 1):

            # 假設兩隊進球數彼此獨立：
            # P(A=a, B=b) = P(A=a) * P(B=b)
            score_probability = (
                team_a_probabilities[team_a_goals] * team_b_probabilities[team_b_goals]
            )

            # 將目前比分機率加入這一個 row
            score_row.append(score_probability)

        # 完成 Team A 某個進球數的整個 row 後，
        # 加入完整 Score Matrix
        score_matrix.append(score_row)
    
    return score_matrix

# ==== 計算比分機率矩陣的總機率 ====
def calculate_score_matrix_probability_sum(score_matrix):
    
    # 儲存所有比分機率的總和
    total_probability = 0.0

    # 逐列讀取 Score Matrix
    for score_row in score_matrix:

        # 將目前這一列的所有比分機率加總
        total_probability += sum(score_row)

    return total_probability

# ==== 計算 Team A Win / Draw / Team B Win 機率 ====
def calculate_match_result_probabilities(score_matrix):

    # 儲存 Team A 勝、和局、Team B 勝的機率
    team_a_win_probability = 0.0
    draw_probability = 0.0
    team_b_win_probability = 0.0

    # 逐列讀取 Score Matrix
    for team_a_goals, score_row in enumerate(score_matrix):

        # 逐一讀取目前 row 中的每一個比分機率
        for team_b_goals, score_probability in enumerate(score_row):

            # Team A 進球數大於 Team B → Team A Win
            if team_a_goals > team_b_goals:
                team_a_win_probability += score_probability

            # 兩隊進球數相同 → Draw
            elif team_a_goals == team_b_goals:
                draw_probability += score_probability

            # Team A 進球數小於 Team B → Team B Win
            else:
                team_b_win_probability += score_probability


    return ( team_a_win_probability, draw_probability, team_b_win_probability )


# ============================
# Independent Test
# ============================

if __name__ == "__main__":

    # 使用目前模型實際產生過的 Lambda 作為獨立測試
    test_lambda = 1.197389

    # 計算 0 ~ 10 球的 Poisson Probability
    goal_probabilities = calculate_goal_probabilities( test_lambda, max_goals=10 )

    print("Test Lambda:")
    print(test_lambda)

    print("Goal Probabilities:")

    # 顯示每一個進球數所對應的機率
    for goals, probability in enumerate(goal_probabilities):

        print( goals, "goals:", probability )

    print("Probability Sum:")
    print( sum(goal_probabilities) )

    # ============================
    # Test Two-team Probabilities
    # ============================

    # 使用目前模型實際產生過的一組 Lambda
    test_lambda_a = 1.197389
    test_lambda_b = 1.187410

    # 分別計算 Team A 與 Team B 的進球機率
    team_a_probabilities, team_b_probabilities = (
        calculate_match_goal_probabilities( test_lambda_a, test_lambda_b, max_goals=10 )
    )

    print("Team A Lambda:")
    print(test_lambda_a)

    print("Team A Probability Sum:")
    print( sum(team_a_probabilities) )

    print("Team B Lambda:")
    print(test_lambda_b)

    print("Team B Probability Sum:")
    print( sum(team_b_probabilities) )

    # ============================
    # Test Score Probability Matrix
    # ============================

    # 使用 Team A 與 Team B 的 Lambda 建立比分機率矩陣
    score_matrix = calculate_score_probability_matrix( test_lambda_a, test_lambda_b, max_goals=10 )

    print("Score Matrix Row Count:")
    print( len(score_matrix) )

    print("Score Matrix Column Count:")
    print( len(score_matrix[0]) )

    # 顯示幾個常見比分的機率
    print("0-0 Probability:")
    print( score_matrix[0][0] )

    print("1-0 Probability:")
    print( score_matrix[1][0] )

    print("0-1 Probability:")
    print( score_matrix[0][1] )

    print("1-1 Probability:")
    print( score_matrix[1][1] )

    print("2-1 Probability:")
    print( score_matrix[2][1] )

    # ============================
    # Validate Score Matrix Probability Sum
    # ============================

    # 將 Score Matrix 中所有比分機率加總
    score_matrix_probability_sum = (
        calculate_score_matrix_probability_sum( score_matrix )
    )

    print("Score Matrix Probability Sum:")
    print( score_matrix_probability_sum )

    # ============================
    # Calculate Match Result Probabilities
    # ============================

    # 將 Score Matrix 中的比分機率，
    # 分別加總成 Team A Win、Draw、Team B Win
    team_a_win_probability, draw_probability, team_b_win_probability = (
        calculate_match_result_probabilities( score_matrix )
    )

    print("Team A Win Probability:")
    print( team_a_win_probability )

    print("Draw Probability:")
    print( draw_probability )

    print("Team B Win Probability:")
    print( team_b_win_probability )

    # ============================
    # Validate Match Result Probability Sum
    # ============================

    # 將 Team A Win、Draw、Team B Win 三種結果機率加總
    match_result_probability_sum = (
        team_a_win_probability
        + draw_probability
        + team_b_win_probability
    )

    print("Match Result Probability Sum:")
    print( match_result_probability_sum )

