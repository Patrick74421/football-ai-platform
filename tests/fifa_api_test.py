import requests
# 匯入正式 Data Cleaner，測試清理後的 Match / Competition 資料
from backend.data_cleaner import (
    prepare_team_data,
    prepare_match_data,
    prepare_competition_data
    )

url = "https://inside.fifa.com/api/data-centre/matches?gender=1&year=2022&language=en&count=1000"

headers = {

        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://inside.fifa.com/data-centre/matches/men?year=2022",
}

response = requests.get(url, headers = headers)

print("Status Code:", response.status_code)

if response.status_code == 200:
    print("Success!")

    # Convert the JSON response into Python data
    data = response.json()

    # Display how many match records were actually returned
    print("Returned Match Count:")
    print(len(data))

    # Count match records with missing or empty match IDs
    empty_id_match_count = 0

    # Count match records with missing or empty competition IDs
    empty_id_competition_count = 0

    # Count records where both match ID and competition ID are empty
    both_empty_count = 0

    # Count records where idMatch is empty but idMatchIfes is also unavailable
    empty_id_match_ifes_count = 0

    # Store idMatchIfes values from old-format match records
    old_match_ifes_ids = []

    # Count old-format match records that also lack idSeason
    empty_id_season_count = 0

    # Count old-format match records that lack competitionName
    empty_competition_name_count = 0

    # Count old-format match records that lack seasonName
    empty_season_name_count = 0

    # Store idSeason values from old-format match records
    old_season_ids = []

    # Store competition names from old-format match records
    old_competition_names = []

    # Store unique season and competition mappings from old-format matches
    old_season_mapping = set()

    for match in data:

        # Check whether idMatch is missing, None, or an empty string
        if not match.get("idMatch"):
            empty_id_match_count += 1

        # Check whether idCompetition is missing, None, or an empty string
        if not match.get("idCompetition"):
            empty_id_competition_count += 1

        # Check whether both IDs are missing or empty in the same record
        if ( not match.get("idMatch") and not match.get("idCompetition") ):
            both_empty_count += 1

        # Check whether an old-format match also lacks idMatchIfes
        if ( not match.get("idMatch") and not match.get("idMatchIfes") ):
            empty_id_match_ifes_count += 1

        # Store idMatchIfes when the record uses the old match format
        if ( not match.get("idMatch") and match.get("idMatchIfes") ):
            old_match_ifes_ids.append( match.get("idMatchIfes") )

        # Check whether an old-format match also lacks idSeason
        if ( not match.get("idMatch") and not match.get("idSeason") ):
            empty_id_season_count += 1

        # Check whether an old-format match lacks competitionName
        if ( not match.get("idMatch") and not match.get("competitionName") ):
            empty_competition_name_count += 1

        # Check whether an old-format match lacks seasonName
        if ( not match.get("idMatch") and not match.get("seasonName") ):
            empty_season_name_count += 1

        # Store season ID and competition name from old-format match records
        if ( not match.get("idMatch") and match.get("idSeason") and match.get("competitionName") ):
            old_season_ids.append( match.get("idSeason") )
            old_competition_names.append( match.get("competitionName")[0]["description"])
        # Store the relationship between season ID, season name, and competition name
        if ( not match.get("idMatch") and match.get("idSeason") and match.get("seasonName") ):
            old_season_mapping.add(
                (
                    match.get("idSeason"),
                    match.get("seasonName")[0]["description"],
                    match.get("competitionName")[0]["description"]
                )
            )

    # Display data quality counts
    print("Empty idMatch Count:")
    print(empty_id_match_count)

    print("Empty idCompetition Count:")
    print(empty_id_competition_count)

    print("Both Empty Count:")
    print(both_empty_count)

    print("Empty idMatchIfes Among Old Matches:")
    print(empty_id_match_ifes_count)

    print("Empty competitionName Among Old Matches:")
    print(empty_competition_name_count)

    print("Empty seasonName Among Old Matches:")
    print(empty_season_name_count)

    # Display the number of unique season IDs among old-format matches
    print("Unique idSeason Count Among Old Matches:")
    print(len(set(old_season_ids)))

    # Display the number of unique competition names among old-format matches
    print("Unique competitionName Count Among Old Matches:")
    print(len(set(old_competition_names)))

    for season_mapping in sorted(old_season_mapping):
        print(season_mapping)

    # Count all old-format idMatchIfes values
    print("Old Match idMatchIfes Count:")
    print(len(old_match_ifes_ids))

    # Count unique old-format idMatchIfes values
    print("Unique Old Match idMatchIfes Count:")
    print(len(set(old_match_ifes_ids)))

    print("Empty idSeason Among Old Matches:")
    print(empty_id_season_count)

    # Display the first match record for basic response verification
    print("First Match:")
    print(data[0])

    # Display the last match record to verify the full date range
    print("Last Match:")
    print(data[-1])

    # ============================
    # Cleaner Verification
    # ============================

    # 使用正式 Cleaner 清理完整的 958 筆 Match API 資料
    clean_match_data = prepare_match_data(data)
    clean_competition_data = prepare_competition_data(data)

    # 顯示 Cleaner 最後產生的 Match / Competition 數量
    print("Clean Match Count:")
    print(len(clean_match_data))

    print("Clean Competition Count:")
    print(len(clean_competition_data))

    # ============================
    # Clean Match Verification
    # ============================

    # 計算清理後仍然沒有 Match ID 的資料
    empty_clean_match_id_count = 0

    # 計算清理後仍然沒有 Competition ID 的 Match
    empty_clean_competition_id_count = 0

    # 計算實際使用 ifes_ fallback 的 Match 數量
    fallback_match_id_count = 0

    # 計算實際使用 season_ fallback Competition ID 的 Match 數量
    fallback_match_competition_count = 0

    # 收集所有清理後的 Match ID，用來檢查是否重複
    clean_match_ids = []

    # 收集 Match 實際使用到的 Competition ID
    clean_match_competition_ids = set()

    for match in clean_match_data:

        # 檢查 fifa_match_id 是否仍然為空
        if not match.get("fifa_match_id"):

            empty_clean_match_id_count += 1

        # 檢查 fifa_competition_id 是否仍然為空
        if not match.get("fifa_competition_id"):

            empty_clean_competition_id_count += 1

        # startswith() 是 Python String method，
        # 用來判斷字串是否以指定文字開頭
        if match.get("fifa_match_id", "").startswith("ifes_"):
            fallback_match_id_count += 1

        # 檢查有多少 Match 使用 season_ fallback
        if match.get("fifa_competition_id", "").startswith("season_"):
            fallback_match_competition_count += 1

        # 收集 Match ID，之後利用 set() 檢查唯一性
        clean_match_ids.append(
            match.get("fifa_match_id")
        )

        # 收集 Match 使用到的 Competition ID
        clean_match_competition_ids.add(
            match.get("fifa_competition_id")
        )


    # ============================
    # Clean Competition Verification
    # ============================

    # 收集 Competition Cleaner 建立的所有 Competition ID
    clean_competition_ids = set()

    # 計算 Cleaner 建立了多少個 season_ fallback Competition
    fallback_competition_id_count = 0

    for competition in clean_competition_data:

        clean_competition_ids.add(
            competition.get("fifa_competition_id")
        )

        if competition.get(
            "fifa_competition_id", ""
        ).startswith("season_"):
            fallback_competition_id_count += 1


    # ============================
    # Match / Competition Relationship Check
    # ============================

    # Set subtraction（集合差集）
    #
    # 找出：
    # Match 使用了哪些 Competition ID，
    # 但是 Competition Cleaner 卻沒有建立
    missing_competition_ids = (
        clean_match_competition_ids - clean_competition_ids
    )


    # ============================
    # Display Cleaner Verification
    # ============================

    print("Empty Clean Match ID Count:")
    print(empty_clean_match_id_count)

    print("Unique Clean Match ID Count:")
    print(len(set(clean_match_ids)))

    print("Empty Clean Competition ID Count:")
    print(empty_clean_competition_id_count)

    print("Fallback Match ID Count:")
    print(fallback_match_id_count)

    print("Fallback Match Competition Count:")
    print(fallback_match_competition_count)

    print("Fallback Competition ID Count:")
    print(fallback_competition_id_count)

    print("Missing Competition IDs Count:")
    print(len(missing_competition_ids))

    print("Missing Competition IDs:")
    print(missing_competition_ids)

    # ============================
    # Team Foreign Key Verification
    # ============================

    # FIFA Team API URL
    team_url = (
        "https://inside.fifa.com/api/data-centre/matches/teams"
        "?gender=1&language=en&year=2022"
    )

    # 取得 FIFA Team 原始資料
    team_response = requests.get(
         team_url,
         headers=headers
    )

    print("Team API Status Code:")
    print(team_response.status_code)

    if team_response.status_code == 200:

        # JSON → Python Team Data
        team_data = team_response.json()

        # 使用正式 Team Cleaner
        clean_team_data = prepare_team_data(team_data)


        print("Clean Team Count:")
        print(len(clean_team_data))

        # ============================
        # Collect Team IDs
        # ============================

        # 儲存 Team API 提供的所有 Team ID
        clean_team_ids = set()

        for team in clean_team_data:
            clean_team_ids.add(
                str(team.get("fifa_team_id"))
            )

        # 儲存 958 場 Match 實際使用到的 Team ID
        match_team_ids = set()

        for match in clean_match_data:
            match_team_ids.add(
                str(match.get("team_a_fifa_id"))
            )

        match_team_ids.add(
            str(match.get("team_b_fifa_id"))
        )

        # ============================
        # Team Relationship Check
        # ============================

        # 找出：
        # Match 使用了，但是 Team API 沒有提供的 Team ID

        missing_team_ids = (
            match_team_ids- clean_team_ids
        )

        # ============================
        # Display Team Verification
        # ============================

        print("Unique Match Team ID Count:")
        print(len(match_team_ids))

        print("Unique Clean Team ID Count:")
        print(len(clean_team_ids))

        print("Missing Team IDs Count:")
        print(len(missing_team_ids))

        print("Missing Team IDs:")
        print(missing_team_ids)

    else:
        print("Team API Request Fail")
        print("Team Response:")
        print(team_response.text)

else:
    print("Request fail")
    print("Response:", response.text)

