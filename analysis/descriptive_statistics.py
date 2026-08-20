def show_score_statistics(match_df):

    # Select score columns used for descriptive statistics
    score_columns = [
        "team_a_score",
        "team_b_score"
    ]

    # Calculate the average score for Team A and Team B
    print("Mean Score:")
    print(match_df[score_columns].mean())

    # Calculate the median score for Team A and Team B
    print("Median Score:")
    print(match_df[score_columns].median())

    # Calculate score standard deviation
    print("Standard Deviation Score:")
    print(match_df[score_columns].std())

    # Find the minimum score
    print("Minimum Score:")
    print(match_df[score_columns].min())

    # Find the maximum score
    print("Maximum Score:")
    print(match_df[score_columns].max())
