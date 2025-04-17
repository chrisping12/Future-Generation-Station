import pandas as pd
import time
from nba_api.stats.endpoints import leaguegamefinder, boxscoreadvancedv2, boxscoretraditionalv2
from nba_api.stats.library.parameters import SeasonAll

"""
    This script uses NBA_API to gathers team data which cannot be located through any log like: 
    'OFF_RATING', 'DEF_RATING', 'E_OFF_RATING', 'E_DEF_RATING', 'AST_PCT', 'REB_PCT']
    and creates a dataframe with those variables recorded for each game.
    
    This code still needs further development to do the same for player data like USG_PCT. 
"""

def get_all_game_ids(season ='2024-25'):
    print("[*] Fetching all game IDs...")
    gf = leaguegamefinder.LeagueGameFinder(season_nullable=season)
    games = gf.get_data_frames()[0]
    games = games[['GAME_ID', 'GAME_DATE']]
    games.drop_duplicates(subset='GAME_ID', inplace=True)
    games['GAME_DATE'] = pd.to_datetime(games['GAME_DATE'])
    return games

def build_team_adv_dataset(season='2024-25', chunk_index=0, num_chunks=7, save_csv=True):
    games_df = get_all_game_ids(season)
    games_df.sort_values('GAME_DATE', inplace=True)
    
    # Split into chunks
    chunk_size = len(games_df) // num_chunks
    start_idx = chunk_index * chunk_size
    end_idx = len(games_df) if chunk_index == num_chunks - 1 else (chunk_index + 1) * chunk_size
    chunk_df = games_df.iloc[start_idx:end_idx].reset_index(drop=True)

    print(f" Processing chunk {chunk_index + 1}/{num_chunks}: {len(chunk_df)} games")

    all_rows = []

    for i, row in chunk_df.iterrows():
        game_id = row['GAME_ID']
        game_date = row['GAME_DATE']

        try:
            print(f"[{i+1}/{len(chunk_df)}] Processing {game_id}")
            box = boxscoreadvancedv2.BoxScoreAdvancedV2(game_id=game_id)
            time.sleep(2.25)
            team_stats = box.get_data_frames()[1]  # TeamStats
            team_stats['GAME_ID'] = game_id
            team_stats['GAME_DATE'] = game_date

            slim = team_stats[[
                'TEAM_ID', 'TEAM_NAME', 'GAME_ID', 'GAME_DATE',
                'OFF_RATING', 'DEF_RATING', 'E_OFF_RATING', 'E_DEF_RATING',
                'AST_PCT', 'REB_PCT', 'PACE', 'E_PACE'
            ]]

            box = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
            team_traditional = box.get_data_frames()[1]  # Team stats
            team_traditional = team_traditional[['TEAM_ID', 'BLK', 'STL', 'PF']]
            team_traditional.columns = ['TEAM_ID', 'TEAM_BLK', 'TEAM_STL', 'TEAM_PF']

            team_stats = pd.merge(team_stats, team_traditional, on='TEAM_ID', how='left')

            # Retain only useful columns including TEAM_BLK etc
            final_stats = team_stats[[
                'TEAM_ID', 'TEAM_NAME', 'GAME_ID', 'GAME_DATE',
                'OFF_RATING', 'DEF_RATING', 'E_OFF_RATING', 'E_DEF_RATING',
                'AST_PCT', 'REB_PCT', 'PACE', 'E_PACE',
                'TEAM_BLK', 'TEAM_STL', 'TEAM_PF'
            ]]

            all_rows.append(final_stats)
            time.sleep(2.250)

        except Exception as e:
            print(f"[!] Error fetching {game_id}: {e}")
            continue


    full_df = pd.concat(all_rows, ignore_index=True)

    if save_csv:
        out_file = f'team_advanced_stats_chunk_{chunk_index + 1}.csv'
        full_df.to_csv(out_file, index=False)
        print(f" Chunk saved to {out_file}")

    return full_df

if __name__ == '__main__':
    
    """Change the 'chunk_index=__' after running each set. Start with 0, then 1, then 2, then 3"""
    
    # Step 1: Run chunk 1
    chunk_df = build_team_adv_dataset(season='2024-25', chunk_index=6, save_csv=True)
    # Preview the output
    print(chunk_df.head())
