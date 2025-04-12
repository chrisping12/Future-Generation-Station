import pandas as pd
#from adv_merger import merge_team_and_player_stats

def merge_team_and_player_stats(player_df, team_df):
    """
    Merges player-level advanced stats with team-level advanced stats
    using GAME_ID and TEAM_ID.
    """
    # Prevent column name collisions
    team_df = team_df.rename(columns={
        'OFF_RATING': 'TEAM_OFF_RATING',
        'DEF_RATING': 'TEAM_DEF_RATING',
        'E_OFF_RATING': 'TEAM_E_OFF_RATING',
        'E_DEF_RATING': 'TEAM_E_DEF_RATING',
        'AST_PCT': 'TEAM_AST_PCT',
        'REB_PCT': 'TEAM_REB_PCT',
        'PACE': 'TEAM_PACE'
    })

    merged_df = pd.merge(
        player_df,
        team_df,
        how='left',
        on=['GAME_ID', 'TEAM_ID']
    )

    return merged_df

# Load combined season-level data
player_df = pd.read_csv("player_advanced_stats_2024-25.csv")
team_df = pd.read_csv("team_advanced_stats_2024-25.csv")

# Clean and filter out invalid TEAM_IDs before converting to int
team_df = team_df[team_df['TEAM_ID'].str.isnumeric()]  # keep only numeric IDs
team_df['TEAM_ID'] = team_df['TEAM_ID'].astype(int)

player_df['TEAM_ID'] = player_df['TEAM_ID'].astype(int)
team_df['TEAM_ID'] = team_df['TEAM_ID'].astype(int)

# Merge
merged_df = merge_team_and_player_stats(player_df, team_df)

merged_df.sort_values(by=['TEAM_ID', 'PLAYER_ID', 'GAME_DATE'], inplace=True)
# Save merged result
merged_df.to_csv("merged_player_team_adv_stats_2024-25.csv", index=False)
print("[✓] Merged player + team stats saved.")


