import pandas as pd

# ==== 新增總進球欄位 ====
def add_total_goals(match_df):

    # Create a copy to avoid modifying the original DataFrame directly
    feature_df = match_df.copy()

    # Calculate the total number of goals scored in each match
    feature_df["total_goals"] = (
        feature_df["team_a_score"] + feature_df["team_b_score"]
    )

    return feature_df

# ==== 新增進球差欄位 ====
def add_goal_difference(feature_df):

    # Create a copy to avoid modifying the input DataFrame directly
    result_df = feature_df.copy()

    # Calculate the goal difference between Team A and Team B
    result_df["goal_difference"] = (
        result_df["team_a_score"] - result_df["team_b_score"]
    )

    return result_df

# ==== 新增比賽結果欄位 ====
def add_match_result(result_df):

    # Create a copy to keep all previously created feature columns
    match_result_df = result_df.copy()

    # Set draw as the default result
    match_result_df["match_result"] = "Draw"

    # Team A wins when the goal difference is greater than zero
    match_result_df.loc[
        match_result_df["goal_difference"] > 0,
        "match_result"
    ] = "Team A Win"

    # Team B wins when the goal difference is less than zero
    match_result_df.loc[
        match_result_df["goal_difference"] < 0,
        "match_result"
    ] = "Team B Win"

    return match_result_df

# ==== 加入 Team A 球隊名稱 ====
def add_team_a_name(match_result_df, team_df):

    # Create a lookup table for Team A
    team_a_lookup_df = team_df[
        ["fifa_team_id", "team_name"]
    ].rename(
        columns={
            "fifa_team_id": "team_a_fifa_id",
            "team_name": "team_a_name"
        }
    )

    # Merge Team A name into match data using FIFA team ID
    team_name_df = match_result_df.merge(
        team_a_lookup_df,
        on="team_a_fifa_id",
        how="left"
    )

    return team_name_df

# ==== 加入 Team B 球隊名稱 ====
def add_team_b_name(team_name_df, team_df):

    # Create a lookup table for Team B
    team_b_lookup_df = team_df[
        ["fifa_team_id", "team_name"]
    ].rename(
        columns={
            "fifa_team_id": "team_b_fifa_id",
            "team_name": "team_b_name"
        }
    )

    # Merge Team B name into match data using FIFA team ID
    team_names_df = team_name_df.merge(
        team_b_lookup_df,
        on="team_b_fifa_id",
        how="left"
    )

    return team_names_df

# ==== 建立球隊視角比賽資料 ====
def create_team_match_data(team_names_df):

    # Create match data from Team A's perspective
    team_a_df = team_names_df[
        [
            "team_a_name",
            "team_b_name",
            "team_a_score",
            "team_b_score"
        ]
    ].rename(
        columns={
            "team_a_name": "team_name",
            "team_b_name": "opponent_name",
            "team_a_score": "goals_for",
            "team_b_score": "goals_against"
        }
    )

    # Create match data from Team B's perspective
    team_b_df = team_names_df[
        [
            "team_b_name",
            "team_a_name",
            "team_b_score",
            "team_a_score"
        ]
    ].rename(
        columns={
            "team_b_name": "team_name",
            "team_a_name": "opponent_name",
            "team_b_score": "goals_for",
            "team_a_score": "goals_against"
        }
    )

    # Combine Team A and Team B perspectives into one DataFrame
    team_match_df = pd.concat(
        [team_a_df, team_b_df],
        ignore_index=True
    )

    return team_match_df


# ==== 新增球隊視角比賽結果欄位 ====
def add_team_match_result(team_match_df):

    # Create a copy to avoid modifying the original team match DataFrame
    team_result_df = team_match_df.copy()

    # Set draw as the default result
    team_result_df["team_result"] = "Draw"

    # Set win when the team scores more goals than the opponent
    team_result_df.loc[
        team_result_df["goals_for"] > team_result_df["goals_against"],
        "team_result"
    ] = "Win"

    # Set loss when the team scores fewer goals than the opponent
    team_result_df.loc[
        team_result_df["goals_for"] < team_result_df["goals_against"],
        "team_result"
    ] = "Loss"

    return team_result_df
