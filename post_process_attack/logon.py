import os 
import random
import pandas as pd

def logon_attack(scenario, company_type, company_type_member, log_root_dir, root_dir, attack_log_dir, output_dir):
    """
    Function to process logon data for a given scenario and company type.
    """

    dates = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    #### load all data ####
    logon_log_path = os.path.join(attack_log_dir, 'logon.csv')

    logon_csvs = pd.read_csv(logon_log_path, encoding='utf-8')
    # print(f"Processing {logon_log_path} with {len(logon_csvs)} rows")
    
    #### fix if instant logon and logout ####
    for i in range(len(logon_csvs)):
        if i > 0:
            sim_time = logon_csvs.loc[i, 'sim_timestamp']
            sim_id = logon_csvs.loc[i, 'id']
            prev_id = logon_csvs.loc[i-1, 'id']
            if sim_id == prev_id:
                prev_sim_time = logon_csvs.loc[i-1, 'sim_timestamp']
                if sim_time == prev_sim_time:
                    # random add near 5 minutes to sim_id
                    new_time = pd.to_datetime(logon_csvs.loc[i, 'sim_timestamp'], format='%H:%M:%S') + pd.Timedelta(seconds=random.randint(30, 200))
                    logon_csvs.loc[i, 'sim_timestamp'] = new_time.strftime('%H:%M:%S')

    starting_date = "2025-05-01"
    
    # get the week number and the date
    daemon_log_path = os.path.join(attack_log_dir, 'daemon_logs')
    daemon_files = os.listdir(daemon_log_path)
    if len(daemon_files) == 0:
        raise FileNotFoundError("No daemon log files found in the specified directory.")
    daemon_file = daemon_files[0]
    week = int(daemon_file.split('_')[2])  # Extract week number from the file name
    date = daemon_file.split('_')[3]
    # get index of date in the dates list
    date_to_add = 7 * (week - 1) + dates.index(date)

    sim_date = pd.to_datetime(starting_date) + pd.Timedelta(days=date_to_add)
    sim_date = sim_date.strftime('%Y-%m-%d')
    
    # apply sim_date to the sim_timestamp
    for i in range(len(logon_csvs)):
        sim_time = pd.to_datetime(logon_csvs.loc[i, 'sim_timestamp'], format='%H:%M:%S')
        logon_csvs.loc[i, 'full_sim_timestamp'] = f"{sim_date} {logon_csvs.loc[i, 'sim_timestamp']}"
        
    sim_idx = logon_csvs.columns.get_loc("sim_timestamp")
    full_sim = logon_csvs.pop("full_sim_timestamp")
    logon_csvs.insert(sim_idx + 1, "full_sim_timestamp", full_sim)

    # rename the column "name" to "user"
    logon_csvs.rename(columns={'name': 'user'}, inplace=True)
    # rename the column "full_sim_timestamp" to "time"
    logon_csvs.rename(columns={'full_sim_timestamp': 'date'}, inplace=True)
    # rename the column "container_id" to "pc"
    logon_csvs.rename(columns={'container_id': 'pc'}, inplace=True)
    # rename the column "status" to "activity"
    logon_csvs.rename(columns={'status': 'activity'}, inplace=True)

    # sorting by time
    logon_csvs = logon_csvs.sort_values(by='date', ascending=True).reset_index(drop=True)

    # before save, check attack
    attack_df = pd.DataFrame(columns=logon_csvs.columns)
    # check for attack pattern
    attack_mask = logon_csvs['id'].str.lower().str.contains(r'\(attack\)')
    # 去掉(attack)标记
    logon_csvs.loc[attack_mask, 'id'] = logon_csvs.loc[attack_mask, 'id'].str.replace(r'\(attack\)', '', case=False, regex=True).str.strip()
    attack_df = logon_csvs[attack_mask].copy()
    
    # if attack_df is not empty, save it to csv, if csv already exists, append to it
    # if not attack_df.empty:
    #     attack_output_path = os.path.join(output_dir, f'{company_type_member}_attack_info.csv')
    #     if os.path.exists(attack_output_path):
    #         attack_df.to_csv(attack_output_path, mode='a', header=False, index=False, encoding='utf-8')
    #     else:
    #         attack_df.to_csv(attack_output_path, header=False, index=False, encoding='utf-8')

    # save full data
    logon_csvs.to_csv(f'{output_dir}/{company_type_member}_logon_full.csv', index=False, encoding='utf-8')

    # remove the column "real_timestamp" and "sim_timestamp"
    logon_csvs.drop(columns=['real_timestamp', 'sim_timestamp'], inplace=True) 

    # save the email_csvs to csv
    logon_csvs.to_csv(f'{output_dir}/{company_type_member}_logon.csv', index=False, encoding='utf-8')
    # logon_csvs.to_csv(f'{output_dir}/{company_type}-logon-full.csv', index=False, encoding='utf-8')