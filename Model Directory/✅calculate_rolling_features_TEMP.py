def _calculate_rolling_features(self, df, player_name):
        feature_rows = []

        def parse_minutes(min_val):
            try:
                if isinstance(min_val, str):
                    if ':' in min_val:
                        parts = min_val.split(':')
                        return int(parts[0]) + int(parts[1]) / 60
                    else:
                        return float(min_val)
                else:
                    return float(min_val)
            except Exception as e:
                print(f"parse_minutes() failed for: {min_val} with error: {e}")
                return 0

        for i in range(self.rolling_window, len(df)):
            current_game = df.iloc[i]
            past_games = df.iloc[i - self.rolling_window:i]
            
            # Get opponent and team IDs
            opp_abbrev = current_game['MATCHUP'].split(' ')[-1]
            player_team_abbrev = current_game['MATCHUP'].split(' ')[0]
            opp_team_id = self.team_abbrev_to_id.get(opp_abbrev, None)
            player_team_id = self.team_abbrev_to_id.get(player_team_abbrev, None)
            
            # Rolling advanced stats from your internal dataset
            rolling_opp_def_5g = get_team_rolling_avg(opp_team_id, current_game['GAME_DATE'], 'TEAM_DEF_RATING')
            rolling_opp_ast_pct_5g = get_team_rolling_avg(opp_team_id, current_game['GAME_DATE'], 'TEAM_AST_PCT')
            rolling_opp_reb_pct_5g = get_team_rolling_avg(opp_team_id, current_game['GAME_DATE'], 'TEAM_REB_PCT')
            rolling_team_off_5g = get_team_rolling_avg(player_team_id, current_game['GAME_DATE'], 'TEAM_OFF_RATING')
            rolling_team_ast_pct_5g = get_team_rolling_avg(player_team_id, current_game['GAME_DATE'], 'TEAM_AST_PCT')
            rolling_team_reb_pct_5g = get_team_rolling_avg(player_team_id, current_game['GAME_DATE'], 'TEAM_REB_PCT')
            latest_team_e_off_rating = get_latest_team_stat(player_team_id, current_game['GAME_DATE'], 'TEAM_E_OFF_RATING')
            latest_opp_e_def_rating = get_latest_team_stat(opp_team_id, current_game['GAME_DATE'], 'TEAM_E_DEF_RATING')

            # Opponent-adjusted projection
            def_rating_scale = get_def_vs_avg_scale(opp_team_id, current_game['GAME_DATE'], stat_col='TEAM_DEF_RATING')
            adjusted_pts_proj_def = past_games['PTS'].mean() * def_rating_scale

            # Rolling shooting + usage efficiency (if these columns exist in game log)
            rolling_usg_pct_5G = past_games['USG_PCT'].dropna().mean() if 'USG_PCT' in past_games.columns else np.nan
            rolling_e_usg_pct_5G = past_games['E_USG_PCT'].mean()
            rolling_fg_pct_5G = past_games['FG_PCT'].mean() if 'FG_PCT' in past_games.columns else np.nan
            rolling_fg3_pct_5G = past_games['FG3_PCT'].mean() if 'FG3_PCT' in past_games.columns else np.nan
            rolling_fga_5G = past_games['FGA'].mean() if 'FGA' in past_games.columns else np.nan
            rolling_poss_5G = past_games['POSS'].mean()
            rolling_e_pace_5G = past_games['E_PACE'].mean()
            rolling_ast_pct_5G = past_games['AST_PCT'].mean()
            rolling_oreb_pct_5G = past_games['OREB_PCT'].mean()
            rolling_dreb_pct_5G = past_games['DREB_PCT'].mean()
            rolling_reb_pct_5G = past_games['REB_PCT'].mean()

            rolling_pts_avg = past_games['PTS'].mean()
            rolling_std = past_games['PTS'].std()
            rolling_3pm_avg = past_games['FG3M'].mean()
            # Fix: Parse MIN correctly
            minutes_list = past_games['MIN'].apply(parse_minutes)
            rolling_min_avg = past_games['MIN'].apply(parse_minutes).mean()
            min_avg = minutes_list.mean()
            last_game_min = parse_minutes(df.iloc[i - 1]['MIN'])
            if last_game_min is not None and rolling_min_avg:
                delta_min_vs_rolling = last_game_min - rolling_min_avg
            else:
                delta_min_vs_rolling = np.nan

            # Safeguards
            fga_safe = max(rolling_fga_5G, 1e-5)
            min_safe = max(min_avg, 1e-5)
            pts_safe = max(rolling_pts_avg, 1e-5)
            three_pm_safe = max(rolling_3pm_avg, 1e-5)

            #-----Ratios-----#
            shots_per_min = rolling_fga_5G / min_safe
            pts_per_fga = rolling_pts_avg / fga_safe
            pts_per_min = rolling_pts_avg / min_safe
            pts_to_3pm_ratio = rolling_pts_avg / three_pm_safe
            ast_to_poss_ratio = rolling_ast_pct_5G / max(rolling_poss_5G, 1e-5)
            usg_to_poss_ratio = rolling_usg_pct_5G / max(rolling_poss_5G, 1e-5)
            engagement_index = (rolling_usg_pct_5G + rolling_ast_pct_5G + rolling_reb_pct_5G) / max(rolling_e_pace_5G, 1e-5)
            volume_efficiency_ratio = rolling_usg_pct_5G * pts_per_fga

            # Delta from last game to rolling averages
            delta_pts_vs_rolling = last_game_pts - past_games['PTS'].mean()
            delta_min_vs_rolling = last_game_min - min_avg
            pts_trend_slope_5G = past_games['PTS'].iloc[-1] - past_games['PTS'].iloc[0]
            opp_def_trend_delta = latest_opp_e_def_rating - rolling_opp_def_5g if rolling_opp_def_5g and latest_opp_e_def_rating else np.nan
            adjusted_pts_proj_usg = (
                past_games['PTS'].mean()
                * (def_rating_scale if not np.isnan(def_rating_scale) else 1.0)
                * (rolling_usg_pct_5G if not np.isnan(rolling_usg_pct_5G) else 1.0)
            )

            # --- Boolean/Flag Features --- #
            is_volume_shooter = int(rolling_fga_5G >= 15)
            is_trending_up = int(pts_trend_slope_5G > 0)
            is_trending_down = int(pts_trend_slope_5G < 0)
            high_efficiency = int(pts_per_fga >= 1.25)

            # Fetch team-level advanced stats
            team_stats = self.team_advanced_stats.get(player_team_id, {})
            opp_stats = self.team_advanced_stats.get(opp_team_id, {})
            team_pace = team_stats.get('TEAM_PACE', np.nan)
            opp_pace = opp_stats.get('TEAM_PACE', np.nan)
            avg_game_pace = np.nanmean([team_pace, opp_pace])

            last_game_pts = df.iloc[i - 1]['PTS']
            
            

            row = {
                'PLAYER_NAME': player_name,
                'Player_ID': current_game['Player_ID'],
                'GAME_DATE': current_game['GAME_DATE'],
                'TEAM_ID': player_team_id,
                'OPP_TEAM_ID': opp_team_id,
                'HOME_AWAY': 0 if '@' in current_game['MATCHUP'] else 1,

                'rolling_pts_avg_5G': rolling_pts_avg,
                'rolling_pts_median_5G': past_games['PTS'].median(),
                'rolling_3pm_avg_5G': rolling_3pm_avg,
                'rolling_3pm_median_5G': past_games['FG3M'].median(),
                'rolling_min_avg_5G': min_avg,
                'rolling_std_pts_5G': rolling_std,
                'pts_consistency_score': rolling_pts_avg / (rolling_std + 1e-5),
                'rest_days': (current_game['GAME_DATE'] - df.iloc[i - 1]['GAME_DATE']).days,
                'is_b2b': int((current_game['GAME_DATE'] - df.iloc[i - 1]['GAME_DATE']).days == 1),
                'rolling_opp_def_rating_5G': rolling_opp_def_5g,
                'rolling_opp_ast_pct_5G': rolling_opp_ast_pct_5g,
                'rolling_team_off_rating_5G': rolling_team_off_5g,
                'rolling_team_reb_pct_5G': rolling_team_reb_pct_5g,
                'team_pace': team_pace,
                'opp_pace': opp_pace,
                'avg_game_pace': avg_game_pace,
                'rolling_team_ast_pct_5G': rolling_team_ast_pct_5g,
                'rolling_opp_reb_pct_5G': rolling_opp_reb_pct_5g,
                'latest_team_e_off_rating': latest_team_e_off_rating,
                'latest_opp_e_def_rating': latest_opp_e_def_rating,
                'adjusted_pts_proj_def': adjusted_pts_proj_def,
                'rolling_usg_pct_5G': rolling_usg_pct_5G,
                'rolling_fg_pct_5G': rolling_fg_pct_5G,
                'rolling_fg3_pct_5G': rolling_fg3_pct_5G,
                'rolling_fga_5G': rolling_fga_5G,
                'delta_pts_vs_rolling': delta_pts_vs_rolling,
                'delta_min_vs_rolling': delta_min_vs_rolling,
                'opp_def_trend_delta': opp_def_trend_delta,
                'adjusted_pts_proj_usg': adjusted_pts_proj_usg,
                'shots_per_min': shots_per_min,
                'pts_per_fga': pts_per_fga,
                'pts_per_min': pts_per_min,
                'pts_to_3pm_ratio': pts_to_3pm_ratio,
                'pts_trend_slope_5G': pts_trend_slope_5G,
                'is_volume_shooter': is_volume_shooter,
                'is_trending_up': is_trending_up,
                'is_trending_down': is_trending_down,
                'high_efficiency': high_efficiency,
                'rolling_ast_pct_5G': rolling_ast_pct_5G,
                'rolling_oreb_pct_5G': rolling_oreb_pct_5G,
                'rolling_dreb_pct_5G': rolling_dreb_pct_5G,
                'rolling_reb_pct_5G': rolling_reb_pct_5G,
                'ast_to_poss_ratio': ast_to_poss_ratio,
                'usg_to_poss_ratio': usg_to_poss_ratio,
                'engagement_index': engagement_index,
                'volume_efficiency_ratio': volume_efficiency_ratio,
                'starts_as_C': int(current_game.get('START_POSITION') == 'C'),
                'starts_as_G': int(current_game.get('START_POSITION') == 'G'),
                'starts_as_F': int(current_game.get('START_POSITION') == 'F'),
                'is_starter': int(current_game.get('START_POSITION') in ['C', 'G', 'F']),
                'PTS': current_game['PTS']


            }

            feature_rows.append(row)

        return pd.DataFrame(feature_rows)