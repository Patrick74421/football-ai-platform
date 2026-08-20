from analysis.data_loader import load_match_data
from analysis.data_quality import check_data_quality
from analysis.descriptive_statistics import show_score_statistics


def main():

    # Load match data from MySQL and convert it to a Pandas DataFrame
    match_df = load_match_data()

    # Check DataFrame structure and data quality
    check_data_quality(match_df)

    # Show descriptive statistics for match scores
    show_score_statistics(match_df)


if __name__ == "__main__":
    main()
