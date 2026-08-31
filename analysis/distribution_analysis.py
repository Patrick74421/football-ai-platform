import math

# ==== 顯示總進球平均數與變異數 ====
def show_total_goals_mean_variance(match_result_df):

    # Select the total_goals column as a Pandas Series
    total_goals = match_result_df["total_goals"]

    # Calculate the mean of total goals
    mean_goals = total_goals.mean()

    # Calculate sample variance using Pandas default ddof=1
    sample_variance = total_goals.var()

    # Calculate population variance using ddof=0
    population_variance = total_goals.var(ddof=0)

    # Display the calculated statistics
    print("Total Goals Mean:")
    print(mean_goals)

    print("Total Goals Sample Variance:")
    print(sample_variance)

    print("Total Goals Population Variance:")
    print(population_variance)

# ==== 計算 Poisson 機率 ====
def calculate_poisson_probability(lambda_value, k):

    # Calculate the probability of exactly k events using the Poisson PMF
    probability = (
        math.exp(-lambda_value)
        * (lambda_value ** k)
        / math.factorial(k)
    )

    # Return the calculated Poisson probability
    return probability

# ==== 顯示 Poisson 機率表 ====
def show_poisson_probability_table(lambda_value, max_k):

    # Display the Poisson distribution parameter
    print("Poisson Lambda:")
    print(lambda_value)

    # Display the probability for each possible event count
    print("Poisson Probability Table:")

    for k in range(0, max_k + 1):

        # Calculate the Poisson probability for the current k value
        probability = calculate_poisson_probability(
            lambda_value,
            k
        )

        # Display the current event count and its probability
        print(k, probability)

# ==== 比較實際總進球次數與 Poisson 期望次數 ====
def show_poisson_observed_expected(match_result_df):

    # Select the total_goals column as a Pandas Series
    total_goals = match_result_df["total_goals"]

    # Use the observed mean as the Poisson lambda parameter
    lambda_value = total_goals.mean()

    # Count the total number of matches
    match_count = len(total_goals)

    # Get the maximum observed total goals
    max_k = int(total_goals.max())

    # Count the observed frequency for each total goal value
    observed_counts = total_goals.value_counts().sort_index()

    # Display the Poisson distribution parameter
    print("Poisson Lambda:")
    print(lambda_value)

    # Display the observed and expected frequencies
    print("Poisson Observed vs Expected:")
    print("Goals Observed Probability Expected")

    for k in range(0, max_k + 1):

        # Get the observed frequency for the current goal value
        observed = observed_counts.get(k, 0)

        # Calculate the Poisson probability for the current goal value
        probability = calculate_poisson_probability(
            lambda_value,
            k
        )

        # Convert the probability into an expected match count
        expected = probability * match_count

        # Display the comparison for the current goal value
        print(k, observed, probability, expected)

