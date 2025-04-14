import pandas as pd
import time
from nba_api.stats.endpoints import leaguegamefinder, boxscoreadvancedv2, boxscoretraditionalv3, boxscorehustlev2, boxscoreplayertrackv2, boxscoremiscv2
from nba_api.stats.library.parameters import SeasonAll

"""
    This script uses NBA_API to gathers team data which cannot be located through any log like: 
    'OFF_RATING', 'DEF_RATING', 'E_OFF_RATING', 'E_DEF_RATING', 'AST_PCT', 'REB_PCT']
    and creates a dataframe with those variables recorded for each game.
    
    This code still needs further development to do the same for player data like USG_PCT. 
"""

def get_all_game_ids(season='2024-25'):
    print("[*] Fetching all game IDs...")
    # Request only NBA games by setting league_id_nullable to "00"
    gf = leaguegamefinder.LeagueGameFinder(season_nullable=season, league_id_nullable='00')
    games = gf.get_data_frames()[0]
    # If available, you could add an extra filter based on a league id column:
    games = games[games['LEAGUE_ID'] == '00']
    games = games[['GAME_ID', 'GAME_DATE']]
    games.drop_duplicates(subset='GAME_ID', inplace=True)
    games['GAME_DATE'] = pd.to_datetime(games['GAME_DATE'])
    return games

def build_player_adv_dataset(season='2024-25', chunk_index=0, num_chunks=4, save_csv=True):
    games_df = get_all_game_ids(season)
    games_df.sort_values('GAME_DATE', inplace=True)

    # Split into chunks
    chunk_size = len(games_df) // num_chunks
    start_idx = chunk_index * chunk_size
    end_idx = len(games_df) if chunk_index == num_chunks - 1 else (chunk_index + 1) * chunk_size
    chunk_df = games_df.iloc[start_idx:end_idx].reset_index(drop=True)

    print(f"[✓] Processing chunk {chunk_index + 1}/{num_chunks}: {len(chunk_df)} games")
    all_rows = []

    for i, row in chunk_df.iterrows():
        game_id = row['GAME_ID']
        game_date = row['GAME_DATE']

        try:
            print(f"[{i+1}/{len(chunk_df)}] Processing {game_id}")

            # Advanced stats
            adv = boxscoreadvancedv2.BoxScoreAdvancedV2(game_id=game_id).get_data_frames()[0]
            adv = adv[[
                'PLAYER_ID', 'PLAYER_NAME', 'TEAM_ID', 'START_POSITION',
                'E_NET_RATING', 'NET_RATING', 'AST_PCT', 'OREB_PCT', 'DREB_PCT', 'REB_PCT',
                'TM_TOV_PCT', 'USG_PCT', 'E_USG_PCT', 'E_PACE', 'PACE', 'POSS', 'PIE'
            ]]

            # Traditional stats
            trad = boxscoretraditionalv3.BoxScoreTraditionalV3(game_id=game_id).get_data_frames()[0]
            trad['PTS_3'] = trad['FG3M'] * 3
            trad['PTS_2'] = (trad['FGM'] - trad['FG3M']) * 2
            trad['PTS_FT'] = trad['FTM']

            # Hustle
            hustle = boxscorehustlev2.BoxScoreHustleV2(game_id=game_id).get_data_frames()[0]
            hustle = hustle[['PLAYER_ID', 'LOOSE_BALLS_RECOVERED', 'SCREEN_ASSISTS']]

            # Player tracking
            track = boxscoreplayertrackv2.BoxScorePlayerTrackV2(game_id=game_id).get_data_frames()[0]
            track = track[['PLAYER_ID', 'TCHS']]

            # Misc
            misc = boxscoremiscv2.BoxScoreMiscV2(game_id=game_id).get_data_frames()[0]
            misc = misc[['PLAYER_ID', 'PTS_FB']]

            # Merge
            merged = trad.merge(adv, on='PLAYER_ID', how='left') \
                         .merge(hustle, on='PLAYER_ID', how='left') \
                         .merge(track, on='PLAYER_ID', how='left') \
                         .merge(misc, on='PLAYER_ID', how='left')

            merged['GAME_ID'] = game_id
            merged['GAME_DATE'] = game_date

            all_rows.append(merged)
            time.sleep(1.0)

        except Exception as e:
            print(f"[!] Error fetching {game_id}: {e}")
            continue

    full_df = pd.concat(all_rows, ignore_index=True)

    if save_csv:
        out_file = f'player_advanced_stats_chunk_{chunk_index + 1}.csv'
        full_df.to_csv(out_file, index=False)
        print(f"[✓] Chunk saved to {out_file}")

    return full_df

if __name__ == '__main__':
    # Step 1: Run chunk 1
    chunk_df = build_player_adv_dataset(season='2024-25', chunk_index=0, save_csv=True)
    # Preview the output
    print(chunk_df.head())
