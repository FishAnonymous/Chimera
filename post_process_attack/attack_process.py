import os 
import pandas as pd
import json
import ast
import random
from tqdm import tqdm

from logon import logon_attack
from https import attack_https
from emails import attack_email
from files import attack_files

if __name__ == "__main__":
    
    # read four dirs email.csv
    weeks = range(1, 5)
    week_dates = [5, 5, 5, 5] # IMPORTANT!
    week_pointer = 0

    # attack_company_name = "Attack-Tech" # 4: change
    # scenario = "Tech-Company"  # 1: change
    # company_type = "tech" # 2: change
    # company_type_member = "tech_company" # 3: change
    # attacker = "cdev-1"

    # attack_company_name = "Attack-Finance"  # 4: change
    # scenario = "Finance-Company"
    # company_type = "finance"
    # company_type_member = "finance_corporation"
    # attacker = "qres-1"

    attack_company_name = "Attack-Medical"  # 4: change
    scenario = "Medical-Institution"
    company_type_member = "medical_institution"
    company_type = "medical"
    attacker = "his-1"

    # Reading
    log_root_dir = f'/data2/visitor/ASE25/Chimera-Dataset/'
    root_dir = "/data2/visitor/ASE25/Chimera/"

    attack_log_root_dir = f"{log_root_dir}/{attack_company_name}/attack_logs"

    attacks = ["gen_attack_1", "gen_attack_2", "gen_attack_3", "gen_attack_4", "gen_attack_5", "gen_attack_6", "gen_attack_7", "gen_attack_8", "gen_attack_9", "gen_attack_10", "gen_attack_11", "gen_attack_12", "multi_attack_1", "multi_attack_2", "multi_attack_3"]

    output_root_dir = f"{root_dir}/Final-Output/attack_{company_type_member}"
    if not os.path.exists(output_root_dir):
        os.makedirs(output_root_dir)

    # for each dir in attack_log_root_dir
    # for attack in attacks:
    for attack in tqdm(attacks, desc="Processing attacks", leave=True):
        attack_log_dir = f"{attack_log_root_dir}/{attack}_{company_type_member}"

        output_dir = f"{output_root_dir}/{attack}"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # find attack time
        attacker_schedule_time = f"{attack_log_dir}/final_schedule.csv"
        attacker_schedule_df = pd.read_csv(attacker_schedule_time, encoding='utf-8')
        # get the rows with id includes (Attacker)
        attacker_all_df = attacker_schedule_df[attacker_schedule_df['id'].str.contains(attacker)]
        attacker_attack_df = attacker_schedule_df[attacker_schedule_df['id'].str.contains("\(Attack\)")]
        # sort the  attacker_all_df by sim_timestamp, get each attacker_attack_df sim_timestamp and the next sim_timestamp, if the last one, use the last sim_timestamp + 5min
        attacker_all_df = attacker_all_df.sort_values(by='sim_timestamp')
        attacker_attack_df = attacker_attack_df.sort_values(by='sim_timestamp')
        attacker_attack_times = []
        for _, attack_row in attacker_attack_df.iterrows():
            idx = attacker_all_df.index.get_loc(attack_row.name)
            attack_time = pd.to_datetime(attacker_all_df.iloc[idx]['sim_timestamp'])
            if idx < len(attacker_all_df) - 1:
                next_time = pd.to_datetime(attacker_all_df.iloc[idx + 1]['sim_timestamp'])
                while next_time <= attack_time:
                    idx += 1
                    next_time = pd.to_datetime(attacker_all_df.iloc[idx + 1]['sim_timestamp'])
            else:
                next_time = attack_time + pd.Timedelta(minutes=5)
            attacker_attack_times.append((attack_time, next_time))

        # logon
        logon_attack(scenario, company_type, company_type_member, log_root_dir, root_dir, attack_log_dir, output_dir)
        
        # http
        attack_https(scenario, company_type, company_type_member, log_root_dir, root_dir, attack_log_dir, output_dir)
        
        # # email
        attack_email(scenario, company_type, company_type_member, log_root_dir, root_dir, attack_log_dir, output_dir)

        # # files
        attack_files(scenario, company_type, company_type_member, log_root_dir, root_dir, attack_log_dir, output_dir)

        ###### process attack info ######s
        attack_info_path = f"{output_dir}/{company_type_member}_attack_info.csv"

        for attack_times in attacker_attack_times:
            attack_start, attack_end = attack_times

            # logon
            result_logon_df = pd.DataFrame()
            logon_csv = f"{output_dir}/{company_type_member}_logon.csv"
            logon_df = pd.read_csv(logon_csv, encoding='utf-8')
            logon_df['date'] = pd.to_datetime(logon_df['date'])

            mask = (logon_df['date'] >= attack_start) & (logon_df['date'] <= attack_end) & (logon_df['id'].str.contains(attacker, case=False))
            logon_in_range = logon_df[mask]
            if not logon_in_range.empty:
                logon_in_range.insert(0, 'type', 'logon')
                new_order = ['type', 'id', 'date', 'user', 'pc', 'activity']
                logon_in_range = logon_in_range[new_order]
                result_logon_df = pd.concat([result_logon_df, logon_in_range[new_order]], ignore_index=True)
                # print(f"write to {attack}")
                # write to attack_info_path, if exists, append
                if os.path.exists(attack_info_path):
                    result_logon_df.to_csv(attack_info_path, mode='a', header=False, index=False, encoding='utf-8')
                else:
                    result_logon_df.to_csv(attack_info_path, mode='w', header=False, index=False, encoding='utf-8')
        
            # # http
            result_http_df = pd.DataFrame()
            http_csv = f"{output_dir}/{company_type_member}_http.csv"
            http_df = pd.read_csv(http_csv, encoding='utf-8')
            http_df['date'] = pd.to_datetime(http_df['date'])

            mask = (http_df['date'] >= attack_start) & (http_df['date'] <= attack_end) & (http_df['id'].str.contains(attacker, case=False))
            http_in_range = http_df[mask]
            if not http_in_range.empty:
                http_in_range.insert(0, 'type', 'http')
                new_order = ['type', 'id', 'date', 'user', 'pc', 'url', 'content']
                http_in_range = http_in_range[new_order]
                result_http_df = pd.concat([result_http_df, http_in_range[new_order]], ignore_index=True)
                # print(f"write to {attack}")
                # write to attack_info_path, if exists, append
                if os.path.exists(attack_info_path):
                    result_http_df.to_csv(attack_info_path, mode='a', header=False, index=False, encoding='utf-8')
                else:
                    result_http_df.to_csv(attack_info_path, mode='w', header=False, index=False, encoding='utf-8')
            
            # email
            result_email_df = pd.DataFrame()
            email_csv = f"{output_dir}/{company_type_member}_email.csv"
            email_df = pd.read_csv(email_csv, encoding='utf-8')
            email_df['date'] = pd.to_datetime(email_df['date'])

            mask = (email_df['date'] >= attack_start) & (email_df['date'] <= attack_end) & (email_df['id'].str.contains(attacker, case=False))
            email_in_range = email_df[mask]
            if not email_in_range.empty:
                email_in_range.insert(0, 'type', 'email')
                new_order = ['type', 'id', 'date', 'user', 'pc', 'subject', 'content']
                email_in_range = email_in_range[new_order]
                result_email_df = pd.concat([result_email_df, email_in_range[new_order]], ignore_index=True)
                # print(f"write to {attack}")
                # write to attack_info_path, if exists, append
                if os.path.exists(attack_info_path):
                    result_email_df.to_csv(attack_info_path, mode='a', header=False, index=False, encoding='utf-8')
                else:
                    result_email_df.to_csv(attack_info_path, mode='w', header=False, index=False, encoding='utf-8')