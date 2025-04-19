import pandas as pd 
from _team_stat_helpers import get_team_stats_df

def enrich_with_adv_player_stats(past_games):
    """
    Enriches the given past_games DataFrame with advanced player-level stats
    like USG_PCT, POSS, E_PACE from the merged CSV (loaded via team_stat_helpers).
    Merges on PLAYER_ID and GAME_DATE.
    """
    adv_df = get_team_stats_df()
    if adv_df is None:
        raise RuntimeError("Advanced stats not loaded. Call load_team_stats() first.")

    # Strip column names
    adv_df.columns = adv_df.columns.str.strip()
    past_games.columns = past_games.columns.str.strip()

    #print(past_games.columns.tolist()),

    # Columns to pull in
    adv_columns = [
    'PLAYER_ID', 'GAME_DATE', 
    'AST_PCT', 'OREB_PCT', 'REB_PCT', 'DREB_PCT', 
    'TEAM_E_PACE', 'POSS', 'USG_PCT', 'START_POSITION',
    'TEAM_BLK', 'TEAM_STL', 'TEAM_PF', 'PTS_3', 'PTS_2', 'PTS_FT',
    'LOOSE_BALLS_RECOVERED', 'SCREEN_ASSISTS','TCHS', 'PTS_FB'
    ]
    
    # Inner join on PLAYER_ID and GAME_DATE
    enriched = pd.merge(
        past_games,
        adv_df[adv_columns],
        on=['PLAYER_ID', 'GAME_DATE'],
        how='left',
        suffixes=('', '_ADV')
    )

    return enriched

def enrich_current_game_with_adv_stats(current_game):
    """
    Enriches a single game row with advanced stats from the merged CSV.
    Expects current_game to be a Series with PLAYER_ID and GAME_DATE.
    """
    adv_df = get_team_stats_df()
    if adv_df is None:
        raise RuntimeError("Advanced stats not loaded. Call load_team_stats() first.")

    adv_df.columns = adv_df.columns.str.strip()
    player_id = current_game['PLAYER_ID']
    game_date = pd.to_datetime(current_game['GAME_DATE'])

    # Filter down to matching player + game
    match = adv_df[
        (adv_df['PLAYER_ID'] == player_id) &
        (adv_df['GAME_DATE'] == game_date)
    ]
    #print(match.head())
    if match.empty:
        print(f"[!] No advanced stats found for PLAYER_ID {player_id} on {game_date.date()}")
        return current_game  # Return original, unmodified

    # Add each matching stat to the row
    for stat in ['AST_PCT', 'OREB_PCT', 'REB_PCT', 'DREB_PCT', 'E_PACE', 'POSS', 'TEAM_BLK', 'TEAM_STL', 'TEAM_PF', 'START_POSITION']:
        if stat in match.columns:
            current_game[stat] = match[stat].values[0]

    return current_game