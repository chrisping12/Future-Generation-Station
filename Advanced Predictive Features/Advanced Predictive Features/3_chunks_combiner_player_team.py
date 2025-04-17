import os
import pandas as pd

def combine_chunks(data_type, num_chunks=4, season='2024-25'):
    """
    Combines multiple CSV chunks for either 'player' or 'team' into one final dataset.
    
    Parameters:
        data_type (str): 'player' or 'team'
        num_chunks (int): Number of chunks saved previously
        season (str): Season string (used in output filename)
    """
    prefix = f"{data_type}_advanced_stats"
    all_chunks = []

    for i in range(1, num_chunks + 1):
        chunk_path = f"{prefix}_chunk_{i}.csv"
        if not os.path.exists(chunk_path):
            print(f"[!] Warning: {chunk_path} not found. Skipping.")
            continue

        print(f"[+] Loading: {chunk_path}")
        df = pd.read_csv(chunk_path)
        all_chunks.append(df)

    if not all_chunks:
        print(f"[!] No valid chunks found for {data_type}.")
        return

    full_df = pd.concat(all_chunks, ignore_index=True)
    output_path = f"{prefix}_{season}.csv"
    full_df.to_csv(output_path, index=False)
    print(f"[✓] Saved combined {data_type} data to: {output_path}")

if __name__ == '__main__':
    combine_chunks(data_type='team', num_chunks=7, season='2024-25')
    combine_chunks(data_type='player', num_chunks=11, season='2024-25')