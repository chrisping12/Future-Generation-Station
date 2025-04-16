import pandas as pd 
from team_stat_helpers import get_team_stats_df

def enrich_with_adv_player_stats(past_games):
    """
    Enrich a DataFrame of past_games with player-level advanced stats.
    """
    adv_df = get_team_stats_df()
    if adv_df is None:
        raise RuntimeError("Advanced stats not loaded. Call load_team_stats() first.")

    # --- Data Cleanup & Type Alignment ---
    adv_df.columns = adv_df.columns.str.strip()
    past_games.columns = past_games.columns.str.strip()

    # Drop duplicate-suffixed columns if they exist
    for col in ['PLAYER_ID_y', 'TEAM_ID_y', 'START_POSITION_y']:
        if col in adv_df.columns:
            adv_df.drop(columns=col, inplace=True)

    # Rename '_x' suffixes to original names
    adv_df.rename(columns=lambda x: x.replace('_x', '') if x.endswith('_x') else x, inplace=True)

    # Align column types for safe merge
    adv_df['PLAYER_ID'] = adv_df['PLAYER_ID'].astype(str)
    past_games['PLAYER_ID'] = past_games['PLAYER_ID'].astype(str)

    adv_df['GAME_DATE'] = pd.to_datetime(adv_df['GAME_DATE']).dt.normalize()
    past_games['GAME_DATE'] = pd.to_datetime(past_games['GAME_DATE']).dt.normalize()

    adv_columns = [
        'PLAYER_ID', 'GAME_DATE',
        'AST_PCT', 'OREB_PCT', 'REB_PCT', 'DREB_PCT',
        'USG_PCT', 'E_USG_PCT', 'E_PACE', 'POSS'
    ]

    # Drop any extra columns to prevent overlap issues during merge
    adv_subset = adv_df[adv_columns].drop_duplicates(subset=['PLAYER_ID', 'GAME_DATE'])

    try:
        enriched = pd.merge(
            past_games,
            adv_subset,
            on=['PLAYER_ID', 'GAME_DATE'],
            how='left',
            suffixes=('', '_adv')
        )
        return enriched
    except Exception as e:
        print(f"[!] Failed to merge advanced stats with past_games: {e}")
        return past_games  # Return unmerged to keep moving

def enrich_current_game_with_adv_stats(current_game):
    """
    Enriches a single game row with advanced stats from the merged CSV.
    Expects current_game to be a Series with PLAYER_ID and GAME_DATE.
    """
    adv_df = get_team_stats_df()
    if adv_df is None:
        raise RuntimeError("Advanced stats not loaded. Call load_team_stats() first.")

    # Strip whitespace just in case
    adv_df.columns = adv_df.columns.str.strip()

    # Drop duplicate-suffixed columns if they exist
    for col in ['PLAYER_ID_y', 'TEAM_ID_y', 'START_POSITION_y']:
        if col in adv_df.columns:
            adv_df.drop(columns=col, inplace=True)

    adv_df.rename(columns=lambda x: x.replace('_x', '') if x.endswith('_x') else x, inplace=True)

    # Ensure PLAYER_ID is str in both for matching
    adv_df['PLAYER_ID'] = adv_df['PLAYER_ID'].astype(str)
    player_id = str(current_game['PLAYER_ID'])

    # Ensure GAME_DATE is datetime in both
    adv_df['GAME_DATE'] = pd.to_datetime(adv_df['GAME_DATE']).dt.normalize()
    game_date = pd.to_datetime(current_game['GAME_DATE']).normalize()

    # Try to match by PLAYER_ID and GAME_DATE
    match = adv_df[
        (adv_df['PLAYER_ID'] == player_id) &
        (adv_df['GAME_DATE'] == game_date)
    ]

    if match.empty:
        similar_dates = adv_df[adv_df['PLAYER_ID'] == player_id]['GAME_DATE'].dt.date.unique()
        print(f"[!] No advanced stats found for PLAYER_ID {player_id} on {game_date.date()} — Available dates: {list(similar_dates)}")
        return current_game

    # Copy over desired fields
    for stat in ['AST_PCT', 'OREB_PCT', 'REB_PCT', 'DREB_PCT', 'USG_PCT', 'E_USG_PCT', 'E_PACE', 'POSS']:
        if stat in match.columns:
            current_game[stat] = match.iloc[0][stat]

    return current_game