import matplotlib.pyplot as plt

# ==== 繪製比賽結果長條圖 ====
def plot_match_result_bar_chart(match_result_df):

    # Count the number of matches in each result category
    result_counts = match_result_df["match_result"].value_counts()

    # Create a bar chart using result categories and their counts
    plt.bar(
        result_counts.index,
        result_counts.values
    )

    # Set the chart title and axis labels
    plt.title("Match Result Distribution")
    plt.xlabel("Match Result")
    plt.ylabel("Number of Matches")

    # Adjust the layout to prevent labels from being cut off
    plt.tight_layout()

    # Display the chart
    plt.show()

# ==== 繪製總進球直方圖 ====
def plot_total_goals_histogram(match_result_df):

    # Get the maximum total goals to define histogram bins
    max_goals = match_result_df["total_goals"].max()

    # Create histogram bins for each possible integer goal count
    bins = range(0, max_goals + 2)

    # Create a histogram of total goals scored per match
    plt.hist(
        match_result_df["total_goals"],
        bins=bins
    )

    # Set the chart title and axis labels
    plt.title("Total Goals Distribution")
    plt.xlabel("Total Goals")
    plt.ylabel("Number of Matches")

    # Adjust the layout to prevent labels from being cut off
    plt.tight_layout()

    # Display the chart
    plt.show()

# ==== 繪製球隊平均進球與平均失球圖 ====
def plot_team_goal_averages(team_match_df):

    # Calculate average goals scored and conceded for each team
    team_goal_averages = (
        team_match_df.groupby("team_name")[
            [
                "goals_for",
                "goals_against"
            ]
        ].mean()
    )

    # Create a grouped bar chart for average goals scored and conceded
    team_goal_averages.plot(
        kind="bar"
    )

    # Set the chart title and axis labels
    plt.title("Team Average Goals")
    plt.xlabel("Team")
    plt.ylabel("Average Goals")

    # Adjust the layout to prevent labels from being cut off
    plt.tight_layout()

    # Display the chart
    plt.show()

# ==== 繪製球隊勝和負分布圖 ====
def plot_team_result_distribution(team_result_df):

    # Count Win, Draw, and Loss results for each team
    team_result_counts = (
        team_result_df.groupby(["team_name", "team_result"])
        .size()
        .unstack(fill_value=0)
    )

    # Create a stacked bar chart for each team's match results
    team_result_counts.plot(
        kind="bar",
        stacked=True
    )

    # Set the chart title and axis labels
    plt.title("Team Win Draw Loss Distribution")
    plt.xlabel("Team")
    plt.ylabel("Number of Matches")

    # Adjust the layout to prevent labels from being cut off
    plt.tight_layout()

    # Display the chart
    plt.show()

