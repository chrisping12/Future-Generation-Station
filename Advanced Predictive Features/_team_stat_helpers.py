import pandas as pd
import numpy as np
import glob

_team_stats_df = None  # Global variable

def load_team_stats(filepath='merged_player_team_adv_stats_2024-25.csv'):
    global _team_stats_df
    _team_stats_df = pd.read_csv(filepath, parse_dates=['GAME_DATE'])
    _team_stats_df.columns = _team_stats_df.columns.str.strip()  # Normalize
    print(f"[✓] Loaded team stats with {len(_team_stats_df)} rows.")

def get_team_rolling_avg(team_id, current_game_date, stat_col, window=5):
    if _team_stats_df is None:
        raise RuntimeError("Team stats not loaded. Call load_team_stats() first.")

    df = _team_stats_df.copy()
    df = df[df['TEAM_ID'] == team_id]
    df = df[df['GAME_DATE'] < pd.to_datetime(current_game_date)]
    df = df.sort_values('GAME_DATE')

    if stat_col not in df.columns:
        print(f"[WARN] Column '{stat_col}' not found in team stats.")
        return np.nan

    if df.empty:
        print(f"[WARN] No games found for TEAM_ID {team_id} before {current_game_date}.")
        return np.nan

    return df[stat_col].tail(window).mean()

def get_t__team_rolling_avg(team_id, current_game_date, stat_col, window=5):
    if _team_stats_df is None:
        raise RuntimeError("Team stats not loaded. Call load_team_stats() first.")

    df = _team_stats_df.copy()

    # Filter for the right team
    df = df[df['TEAM_ID'] == team_id]

    # Only keep numeric columns + GAME_DATE
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols += ['GAME_DATE']  # Keep GAME_DATE for grouping
    df = df[numeric_cols]

    # Group by GAME_DATE and average
    df = df.groupby('GAME_DATE').mean().reset_index()

    # Filter games before current
    df = df[df['GAME_DATE'] < pd.to_datetime(current_game_date)]
    df = df.sort_values('GAME_DATE')

    if stat_col not in df.columns or df.empty:
        return np.nan

    return df[stat_col].tail(window).mean()


def get_latest_team_stat(team_id, current_game_date, stat_col):
    if _team_stats_df is None:
        raise RuntimeError("Team stats not loaded. Call load_team_stats() first.")

    df = _team_stats_df.copy()
    df = df[df['TEAM_ID'] == team_id]
    df = df[df['GAME_DATE'] < pd.to_datetime(current_game_date)]
    df = df.sort_values('GAME_DATE')

    if stat_col not in df.columns or df.empty:
        return np.nan

    return df.iloc[-1][stat_col]

def get_def_vs_avg_scale(opp_team_id, game_date, stat_col='TEAM_DEF_RATING'):
    """
    This is for opponent defense adjustment based on how much they hold players below their season average.
    Returns scale factor: league_avg_stat / opponent_recent_stat
    Example: If opp_def_rating is low, this will return a multiplier < 1
    """
    if _team_stats_df is None:
        raise RuntimeError("Team stats not loaded. Call load_team_stats() first.")

    df = _team_stats_df.copy()
    df = df[df['TEAM_ID'] == opp_team_id]
    df = df[df['GAME_DATE'] < pd.to_datetime(game_date)]
    df = df.sort_values('GAME_DATE')

    if stat_col not in df.columns or len(df) < 5:
        return 1.0  # Default scaling

    # Compare most recent value to 5-game average before it
    last_val = df[stat_col].iloc[-1]
    rolling_avg = df[stat_col].iloc[-6:-1].mean()

    if np.isnan(last_val) or np.isnan(rolling_avg) or rolling_avg == 0:
        return 1.0

    return last_val / rolling_avg

def get_team_stats_df():
    global _team_stats_df
    return _team_stats_df

load_team_stats("merged_player_team_adv_stats_2024-25.csv")