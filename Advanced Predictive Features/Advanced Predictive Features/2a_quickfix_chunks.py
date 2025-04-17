import pandas as pd
import os

# G-League TEAM_IDs to remove
g_league_team_ids = [
    1612709931, 1612709913, 1612709902, 1612709917, 
    1612709889, 1612709922, 1612709914, 1612709905,
    1612709919, 1612709918, 1612709909, 1612709927,
    1612709920, 1612709911, 1612709915, 1612709929,
    1612709928, 1612709933, 1612709904, 1612709921, 
    1612709890, 1612709923, 1612709908, 1612709910,
    1612709903, 1612709893, 1612709932, 1612709934,
    1612709924, 1612709925, 1612709926
]

# CSV files to clean
csv_files = [
    "team_advanced_stats_chunk_1.csv",
    "team_advanced_stats_chunk_2.csv",
    "team_advanced_stats_chunk_3.csv",
    "team_advanced_stats_chunk_4.csv",
    "player_advanced_stats_chunk_1.csv",
    "player_advanced_stats_chunk_2.csv",
    "player_advanced_stats_chunk_3.csv",
    "player_advanced_stats_chunk_4.csv",
]

# Loop through each file, clean it, and save it
for file in csv_files:
    try:
        df = pd.read_csv(file)
        if 'TEAM_ID' not in df.columns:
            print(f"[!] Skipping {file}: No 'TEAM_ID' column found.")
            continue

        before = len(df)
        df_cleaned = df[~df['TEAM_ID'].isin(g_league_team_ids)]
        after = len(df_cleaned)

        new_filename = file.replace(".csv", "_CLEANED.csv")
        df_cleaned.to_csv(new_filename, index=False)
        print(f"[✓] Cleaned {file}: {before - after} G-League rows removed, saved to {new_filename}")
        
    except Exception as e:
        print(f"[!] Failed to clean {file}: {e}")