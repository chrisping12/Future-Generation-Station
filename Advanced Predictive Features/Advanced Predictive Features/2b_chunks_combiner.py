import pandas as pd

# Step 1: Load all 4 chunks
df1 = pd.read_csv("team_advanced_stats_chunk_1.csv")
df2 = pd.read_csv("team_advanced_stats_chunk_2.csv")
df3 = pd.read_csv("team_advanced_stats_chunk_3.csv")
df4 = pd.read_csv("team_advanced_stats_chunk_4.csv")

# Step 2: Combine into one DataFrame
full_df = pd.concat([df1, df2, df3, df4], ignore_index=True)

# Step 3: Drop G-League rows by team name (safe filter)
g_league_teams = [
    1612709931, 1612709913, 1612709902, 1612709917, 
    1612709889, 1612709922, 1612709914, 1612709905,
    1612709919, 1612709918, 1612709909, 1612709927,
    1612709920, 1612709911, 1612709915, 1612709929,
    1612709928, 1612709933, 1612709904, 1612709921, 
    1612709890, 1612709923, 1612709908, 1612709910,
    1612709903, 1612709893, 1612709932, 1612709934,
    1612709924, 1612709925, 1612709926, 
]

cleaned_df = full_df[~full_df['TEAM_ID'].isin(g_league_teams)]

# Step 4: Save cleaned file
cleaned_df.to_csv("team_advanced_stats_2024-25.csv", index=False)
print(f"[✓] Saved NBA-only advanced stats with {len(cleaned_df)} rows.")

