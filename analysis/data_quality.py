def check_data_quality(match_df):

    # Check the number of rows and columns
    print("Shape:")
    print(match_df.shape)

    # Preview the first five records
    print("Head:")
    print(match_df.head())

    # Check all DataFrame column names
    print("Columns:")
    print(match_df.columns)

    # Check column data types and non-null values
    print("Info:")
    match_df.info()

    # Count missing values in each column
    print("Missing Values:")
    print(match_df.isnull().sum())

    # Count duplicated rows
    print("Duplicate Rows:")
    print(match_df.duplicated().sum())

def check_data_quality(match_df):
                                                                                    # Check the number of rows and columns
    print("Shape:")
    print(match_df.shape)

    # Preview the first five records
    print("Head:")
    print(match_df.head())

    # Check all DataFrame column names
    print("Columns:")
    print(match_df.columns)

    # Check column data types and non-null values
    print("Info:")
    match_df.info()

    # Count missing values in each column
    print("Missing Values:")
    print(match_df.isnull().sum())

    # Count duplicated rows
    print("Duplicate Rows:")
    print(match_df.duplicated().sum())
