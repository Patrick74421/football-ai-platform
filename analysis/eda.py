from analysis.data_loader import (
    load_match_data,
    load_team_data
)
from analysis.data_quality import check_data_quality
from analysis.descriptive_statistics import show_score_statistics
from analysis.feature_engineering import (
    add_total_goals,
    add_goal_difference,
    add_match_result,
    add_team_a_name,
    add_team_b_name,
    create_team_match_data,
    add_team_match_result
)
from analysis.football_analysis import (
    show_match_result_counts,
    show_match_result_percentage,
    show_average_total_goals,
    show_total_goals_distribution,
    show_team_match_counts,
    show_team_goal_totals,
    show_team_goal_averages,
    show_team_result_counts
)
from analysis.visualization import (
    plot_match_result_bar_chart,
    plot_total_goals_histogram,
    plot_team_goal_averages,
    plot_team_result_distribution
)
from analysis.distribution_analysis import (
    show_total_goals_mean_variance,
    show_poisson_observed_expected
)

def main():

    # Load match data from MySQL and convert it to a Pandas DataFrame
    match_df = load_match_data()

    # Load team data from MySQL
    team_df = load_team_data()

    # Check DataFrame structure and data quality
    check_data_quality(match_df)

    # Show descriptive statistics for match scores
    show_score_statistics(match_df)

    # Create football analysis features from the original match data
    feature_df = add_total_goals(match_df)

    # Create the goal_difference feature while keeping previous features
    result_df = add_goal_difference(feature_df)

    # Create the match_result feature while keeping previous features
    match_result_df = add_match_result(result_df)

    # Add Team A name to match data
    team_name_df = add_team_a_name(
        match_result_df,
        team_df
    )

    # Add Team B name to match data
    team_names_df = add_team_b_name(
        team_name_df,
        team_df
    )

    # Create match records from each team's perspective
    team_match_df = create_team_match_data(
        team_names_df
    )

    # Add win, draw, or loss result from each team's perspective
    team_result_df = add_team_match_result(team_match_df)


    # Preview the newly created total_goals feature
    print("Match Goals:")
    print(
        match_result_df[
            [
                "team_a_score",
                "team_b_score",
                "total_goals",
                "goal_difference",
                "match_result"
            ]
        ].head().to_string(index=False)
    )

    # Show the number of matches for each result category
    show_match_result_counts(match_result_df)

    # Show the percentage of each match result category
    show_match_result_percentage(match_result_df)

    # Show the average total goals scored per match
    show_average_total_goals(match_result_df)

    # Show the distribution of total goals per match
    show_total_goals_distribution(match_result_df)

    # Show mean and variance of total goals for distribution analysis
    show_total_goals_mean_variance(match_result_df)

    # Compare observed total goal frequencies with Poisson expected frequencies
    show_poisson_observed_expected(match_result_df)

    # Display Team A and Team B names
    print("Match Team Names:")
    print(
        team_names_df[
            [
                "team_a_name",
                "team_b_name"
            ]
        ].head().to_string(index=False)
    )

    # Display team-perspective match data
    print("Team Match Data:")
    print(team_match_df.head(10).to_string(index=False))

    # Show the number of matches played by each team
    show_team_match_counts(team_match_df)

    # Show total goals scored and conceded by each team
    show_team_goal_totals(team_match_df)

    # Show average goals scored and conceded per match by each team
    show_team_goal_averages(team_match_df)

    # Show wins, draws, and losses for each team
    show_team_result_counts(team_result_df)

    # Plot the distribution of match results
    plot_match_result_bar_chart(match_result_df)

    # Plot the distribution of total goals per match
    plot_total_goals_histogram(match_result_df)

    # Plot average goals scored and conceded for each team
    plot_team_goal_averages(team_match_df)

    # Plot win, draw, and loss distribution for each team
    plot_team_result_distribution(team_result_df)

if __name__ == "__main__":
    main()
