# ============================
# Team Data Cleaning
# ============================

def prepare_team_data(team_data):

    clean_team_data = []
    error_team_data = []

    expected_keys = {
        "fifa_team_id",
        "association_id",
        "team_name",
        "confederation_id",
        "confederation_name"
    }

    for team in team_data:

        clean_team = {
            "fifa_team_id": team["id"],
            "association_id": team["associationId"],
            "team_name": team["name"],
            "confederation_id": team["confederation"]["id"],
            "confederation_name": team["confederation"]["name"]

        }

        clean_team_data.append(clean_team)

    for team in clean_team_data:

        if set(team.keys()) != expected_keys:
                error_team_data.append(team)

    if len(error_team_data) == 0:
        print("Team 資料欄位正常")

    else:
        print("Team 資料欄位異常")

        for team in error_team_data:
            print(team)


    return clean_team_data

# ============================
# Match Data Cleaning
# ============================

def prepare_match_data(match_data):

    clean_match_data = []
    error_match_data = []

    expected_match_keys = {
        "fifa_match_id",
        "match_date",
        "fifa_competition_id",
        "team_a_fifa_id",
        "team_b_fifa_id",
        "team_a_score",
        "team_b_score"
    }

    for match in match_data:

        # ============================
        # Prepare Match ID
        # ============================

        # 新格式資料直接使用 FIFA idMatch
        if match.get("idMatch"):
            fifa_match_id = match["idMatch"]

        # 舊格式資料改用 idMatchIfes 作為 fallback
        else:
            fifa_match_id = ( "ifes_" + str(match["idMatchIfes"]) )

        # ============================
        # Prepare Competition ID
        # ============================

        # 新格式資料直接使用 FIFA idCompetition
        if match.get("idCompetition"):
            fifa_competition_id = match["idCompetition"]

        # 舊格式資料改用 idSeason 建立 fallback ID
        else:
            fifa_competition_id = ( "season_" + str(match["idSeason"]) )

        # ============================
        # Build Clean Match Data
        # ============================

        # 將 FIFA API 原始 Match 資料整理成專案使用的欄位

        clean_match = {
            #"fifa_match_id": match["idMatch"],
            "fifa_match_id": fifa_match_id,
            "match_date": match["matchDate"],
            #"fifa_competition_id": match["idCompetition"],
            "fifa_competition_id": fifa_competition_id,
            "team_a_fifa_id": match["teamAId"],
            "team_b_fifa_id": match["teamBId"],
            "team_a_score": match["teamAScore"],
            "team_b_score": match["teamBScore"]
        }

        # 將清理完成的 Match 加入結果 List
        clean_match_data.append(clean_match)

    for match in clean_match_data:

        if set(match.keys()) != expected_match_keys:
            error_match_data.append(match)

    if len(error_match_data) == 0:
        print("Match 資料欄位正常")
    else:
        print("Match 資料欄位異常")

        for match in error_match_data:
            print(match)

    return clean_match_data

# ============================
# Competition Data Cleaning
# ============================

def prepare_competition_data(match_data):

    clean_competition_data = []
    error_competition_data = []
    seen_competition_ids = set()

    expected_competition_keys = {
        "fifa_competition_id",
        "competition_name"
    }

    for match in match_data:

        # ============================
        # Prepare Competition Data
        # ============================

        # 新格式資料直接使用 FIFA idCompetition
        if match.get("idCompetition"):

            fifa_competition_id = match["idCompetition"]

            # competitionName 是 List，
            # [0] 取得第一筆 Dictionary，
            # ["description"] 取得賽事名稱
            competition_name = ( match["competitionName"][0]["description"] )

        # 舊格式資料沒有 idCompetition，
        # 改用 idSeason 建立 fallback Competition ID
        else:

            fifa_competition_id = ( "season_" + str(match["idSeason"]) )

            # 舊格式的 competitionName 太粗略，
            # 因此使用 seasonName 作為較完整的賽事名稱
            competition_name = ( match["seasonName"][0]["description"] )

        # ============================
        # Remove Duplicate Competition
        # ============================

        # 如果這個 Competition ID 尚未出現過，
        # 才加入 clean_competition_data

        if fifa_competition_id not in seen_competition_ids:

            clean_competition = {
                "fifa_competition_id": fifa_competition_id,
                "competition_name": competition_name
            }

            # 儲存清理完成的 Competition
            clean_competition_data.append(clean_competition)

            # 將 Competition ID 記錄到 Set，
            # 避免同一個賽事被重複加入
            seen_competition_ids.add(fifa_competition_id)

    for competition in clean_competition_data:

        if set(competition.keys()) != expected_competition_keys:
                error_competition_data.append(competition)

    if len(error_competition_data) == 0:
        print("Competition 資料欄位正常")
    else:
        print("Competition 資料欄位異常")

        for competition in error_competition_data:
            print(competition)


    return clean_competition_data


