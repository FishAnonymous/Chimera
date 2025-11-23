import os 
import pandas as pd
import json
import ast
import re
import json
from tqdm import tqdm
import random
import lorem

def mutate_time(dt):
    # Randomly add or subtract up to 1 minute
    delta = pd.Timedelta(seconds=random.randint(-10, 10))
    return dt + delta

def attack_files(scenario, company_type, company_type_member, log_root_dir, root_dir, attack_log_dir, output_dir):

    output_csv = f'{output_dir}/{company_type_member}_file_raw.csv'

    id_role_map = {}
    id_list = []
    profile_list = []

    #######################
    profile_output_dir = f"{root_dir}/experiment_output/gemini_{company_type_member}/generated_members"
    for file in os.listdir(profile_output_dir):
        if file.endswith(".jsonc"):
            member_profile_path = os.path.join(profile_output_dir, file)
            with open(member_profile_path, 'r') as f:
                member_profile = json.load(f)
            id_role_map[member_profile['id']] = member_profile['role'] # add id-role map
            id_list.append(member_profile['id'])
            profile_list.append(member_profile) # add profile
    #######################

    data_rows = []
    last_url = None

    execution_log_path = attack_log_dir
        
    for member_id in tqdm(id_list, desc=f"Processing member logs", leave=False):    
        user_log_dir = os.path.join(execution_log_path, member_id)

        # for every file inside the user_log_dir, read the file and extract the content and do not read the file with "solution"
        log_files = [f for f in os.listdir(user_log_dir) if f.endswith('.log') and 'solution' not in f]
        for member_action_log in tqdm(log_files, desc=f"Processing logs for {member_id}", leave=False):
            member_action_log_path = os.path.join(user_log_dir, member_action_log)

            with open(member_action_log_path, 'r') as f:
                content = f.readlines()
            for line in content:
                if "'tool_calls': [{'id': 'null', 'type': 'function', 'function': {'name':" in line:
                    match = re.search(r"'name': '([^']+)'", line)

                    time = line.split(',')[0].strip()
                    if match:
                        function_name = match.group(1)
                        # 'tool_calls': [{'id': 'null', 'type':
                        # {'shell_exec', 'browse_url', 'search_duckduckgo', 'file_find_in_content', 'write_to_file', 'search_google', 'file_find_by_name'}
                        if function_name == 'shell_exec':
                            match = re.search(r'"command"\s*:\s*"([^"]+)"', line)
                            if match:
                                command_data = match.group(1)
                                # pass

                        elif function_name == 'file_find_in_content':
                            match = re.search(r"'arguments':\s*'\{\"file\":\s*\"([^\"]+)\"", line)
                            if match:
                                file_read = match.group(1)
                                row = {
                                    'real_timestamp': time,
                                    'id': member_id,
                                    'filename': file_read,
                                    'type': 'read',
                                    'content': lorem.sentence()
                                }
                            data_rows.append(row)
                        
                        elif function_name == 'file_find_by_name':
                            matches = re.findall(r"'arguments':\s*'\{\"glob\":\s*\"([^\"]+)\"", line)
                            for match in matches:
                                file_name = match
                                row = {
                                    'real_timestamp': time,
                                    'id': member_id,
                                    'filename': file_name,
                                    'type': 'read',
                                    'content': lorem.sentence()
                                }
                                data_rows.append(row)
                        
                        elif function_name == 'write_to_file':
                            content_match = re.search(r"'arguments':\s*'\{\"content\":\s*\"([^\"]+)\"", line)
                            filename_match = re.search(r'"filename"\s*:\s*"([^"]+)"', line)

                            row = {
                                'real_timestamp': time,
                                'id': member_id,
                                'filename': filename_match.group(1),
                                'type': 'write',
                                'content': content_match.group(1) if content_match else lorem.sentence()
                            }
                            data_rows.append(row)
                
                if "Content successfully written to file" in line:
                    match = re.search(r"'content': 'Content successfully written to file: ([^']+)'", line)
                    if match:
                        file_written = match.group(1)
                        row = {
                            'real_timestamp': time,
                            'id': member_id,
                            'filename': file_written,
                            'type': 'write',
                            'content': lorem.sentence()
                        }
                        data_rows.append(row)

    df = pd.DataFrame(data_rows)

    df.to_csv(output_csv, index=False, encoding='utf-8')

    # Processing the raw

    raw_csv = f'{output_dir}/{company_type_member}_file_raw.csv'
    output_csv = f'{output_dir}/{company_type_member}_file.csv'

    # reading the raw csv
    raw_df = pd.read_csv(raw_csv, encoding='utf-8')

        # 1. match up with the actual time
    logon_csv = f'{output_dir}/{company_type_member}_logon_full.csv'
    logon_df = pd.read_csv(logon_csv, encoding='utf-8')

    logon_df['real_timestamp'] = pd.to_datetime(logon_df['real_timestamp'])
    logon_df['date'] = pd.to_datetime(logon_df['date'])
    raw_df['real_timestamp'] = pd.to_datetime(raw_df['real_timestamp'])

    raw_df = raw_df.sort_values('real_timestamp')
    logon_df = logon_df.sort_values('real_timestamp')

    result = pd.merge_asof(
        raw_df,
        logon_df,
        on='real_timestamp',
        by='id',
        direction='nearest'
    )

    # # 2. mutate the date time by up to 1 minute
    result['date'] = result['date'].apply(mutate_time)

    # # 3. remove sim_timestamp, real_timestamp, activity
    result.drop(columns=['sim_timestamp', 'real_timestamp', 'activity'], inplace=True)

    # # 4. sort by date
    result = result.sort_values(by='date', ascending=True).reset_index(drop=True)

    result.to_csv(output_csv, index=False, encoding='utf-8')