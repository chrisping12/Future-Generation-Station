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
        'PACE': 'TEAM_PACE',
        'E_PACE': 'TEAM_E_PACE'
    })

    merged_df = pd.merge(
        player_df,
        team_df,
        how='inner',
        on=["TEAM_ID", "GAME_ID"]
    )

    return merged_df

# Load combined season-level data
player_df = pd.read_csv("player_advanced_stats_2024-25.csv")
team_df = pd.read_csv("team_advanced_stats_2024-25.csv")

#print("player_df columns:", player_df.columns.tolist())
#print("team_df columns:", team_df.columns.tolist())

# Clean and filter out invalid TEAM_IDs before converting to int
team_df['TEAM_ID'] = pd.to_numeric(team_df['TEAM_ID'], errors='coerce') # keep only numeric IDs
team_df['TEAM_ID'] = team_df['TEAM_ID'].astype(int)

player_df.rename(columns={"TEAM_ID_x": "TEAM_ID"}, inplace=True)
player_df['TEAM_ID'] = player_df['TEAM_ID'].astype(int)

# Merge
merged_df = merge_team_and_player_stats(player_df, team_df)

merged_df.rename(columns={
    'PLAYER_NAME_x': 'PLAYER_NAME',
    'START_POSITION_x': 'START_POSITION',
    'GAME_DATE_x': 'GAME_DATE'
}, inplace=True)

merged_df.drop(columns=['PLAYER_NAME_y', 'START_POSITION_y', 'GAME_DATE_y', 'TEAM_ID_y'], inplace=True, errors='ignore')
# Rename the columns you want to keep

merged_df.sort_values(by=['TEAM_ID', 'PLAYER_ID', 'GAME_DATE'], inplace=True)
print("merged_df columns:", merged_df.columns.tolist())

# Save merged result
merged_df.to_csv("merged_player_team_adv_stats_2024-25.csv", index=False)
print("Merged player + team stats saved.")


