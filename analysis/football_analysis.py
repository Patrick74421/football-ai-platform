# ==== 統計比賽結果場次 ====
def show_match_result_counts(match_result_df):

    # Count how many matches belong to each result category
    result_counts = match_result_df["match_result"].value_counts()

    # Display the number of Team A wins, draws, and Team B wins
    print("Match Result Counts:")
    print(result_counts)

# ==== 計算比賽結果比例 ====
def show_match_result_percentage(match_result_df):

    # Calculate the percentage of each result category
    result_percentage = (
        match_result_df["match_result"].value_counts(normalize=True) * 100
    )

    # Display the percentage of Team A win, draws, and Team B wins
    print("Match Result Percentage:")
    print(result_percentage)

# ==== 計算每場平均總進球 ====
def show_average_total_goals(match_result_df):

    # Calculate the average total goals scored per match
    average_total_goals = match_result_df["total_goals"].mean()

    # Display the average total goals per match
    print("Average Total Goals:")
    print(average_total_goals)

# ==== 統計每場總進球分布 ====
def show_total_goals_distribution(match_result_df):

    # Count how many matches have each total_goals value
    total_goals_distribution = (
        match_result_df["total_goals"].value_counts().sort_index()
    )

    # Display the distribution of total goals
    print("Total Goals Distribution:")
    print(total_goals_distribution)

# ==== 統計每支球隊出賽場次 ====
def show_team_match_counts(team_match_df):

    # Group match records by team name and count the rows in each group
    team_match_counts = (
        team_match_df.groupby("team_name")
        .size()
        .sort_values(ascending=False)
    )

    # Display the number of matches played by each team
    print("Team Match Counts:")
    print(team_match_counts)

# ==== 統計每支球隊總進球與總失球 ====
def show_team_goal_totals(team_match_df):

    # Group match records by team and sum goals scored and goals conceded
    team_goal_totals = (
        team_match_df.groupby("team_name")[
            [
                "goals_for",
                "goals_against"
            ]
        ].sum()
    )

    # Display total goals scored and conceded by each team
    print("Team Goal Totals:")
    print(team_goal_totals)

# ==== 計算每支球隊平均進球與平均失球 ====
def show_team_goal_averages(team_match_df):

    # Group match records by team and calculate average goals scored and conceded
    team_goal_averages = (
        team_match_df.groupby("team_name")[
            [
                "goals_for",
                "goals_against"
            ]
        ].mean()
    )

    # Display average goals scored and conceded per match by each team
    print("Team Goal Averages:")
    print(team_goal_averages)

# ==== 統計每支球隊勝和負場次 ====
def show_team_result_counts(team_result_df):

    # Group match records by team name and result, then count each result
    team_result_counts = (
        team_result_df.groupby(
            ["team_name", "team_result"]
        )
        .size()
        .unstack(fill_value=0)
    )

    # Display wins, draws, and losses for each team
    print("Team Result Counts:")
    print(team_result_counts)
