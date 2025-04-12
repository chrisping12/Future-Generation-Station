import pandas as pd
import numpy as np

# Global variable to hold loaded data
_team_stats_df = None

def load_team_stats(filepath='team_advanced_stats_2024-25.csv'):
    global _team_stats_df
    _team_stats_df = pd.read_csv(filepath, parse_dates=['GAME_DATE'])
    print(f"[✓] Loaded team stats with {len(_team_stats_df)} rows.")

def get_team_rolling_avg(team_id, game_date, stat_col, window=5):
    if _team_stats_df is None:
        raise ValueError("Team stats data not loaded. Run load_team_stats() first.")

    df = _team_stats_df
    past_games = df[(df['TEAM_ID'] == team_id) & (df['GAME_DATE'] < game_date)]
    past_games = past_games.sort_values('GAME_DATE').tail(window)
    
    if past_games.empty:
        return np.nan
    return past_games[stat_col].mean()

def get_latest_team_stat(team_id, game_date, stat_col):
    if _team_stats_df is None:
        raise ValueError("Team stats data not loaded. Run load_team_stats() first.")

    df = _team_stats_df
    row = df[(df['TEAM_ID'] == team_id) & (df['GAME_DATE'] < game_date)].sort_values('GAME_DATE').tail(1)
    
    if row.empty:
        return np.nan
    return row.iloc[0][stat_col]

def get_def_vs_avg_scale(opponent_id, game_date, stat_col='DEF_RATING'):
    """
    Returns scale factor: league_avg_stat / opponent_recent_stat
    Example: If opp_def_rating is low, this will return a multiplier < 1
    """
    if _team_stats_df is None:
        raise ValueError("Team stats data not loaded. Run load_team_stats() first.")

    df = _team_stats_df
    league_avg = df[df['GAME_DATE'] < game_date][stat_col].mean()
    opponent_avg = get_team_rolling_avg(opponent_id, game_date, stat_col, window=5)

    if np.isnan(opponent_avg) or opponent_avg == 0:
        return 1.0  # No adjustment
    return league_avg / opponent_avg

load_team_stats("team_advanced_stats_2024-25.csv")