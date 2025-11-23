import os 
import pandas as pd
import json
import ast
from tqdm import tqdm
import re
import random
import requests

def clean_url(url):
    return url.rstrip('",\' >}\]\n\r\t')

def mutate_time(dt):
    # Randomly add or subtract up to 1 minute
    delta = pd.Timedelta(seconds=random.randint(-30, 30))
    return dt + delta

# read four dirs email.csv
weeks = range(1, 4)

scenario = "Tech-Company"
company_type_member = "tech_company"
company_type = "tech"
foundation_model = 'openai'

# scenario = "Finance-Company"
# company_type_member = "finance_corporation"
# company_type = "finance"

# scenario = "Medical-Institution"
# company_type_member = "medical_institution"
# company_type = "medical"

root_dir = "/data2/visitor/ASE25/Chimera"

output_dir = f"{root_dir}/Final-Output-OpenAI/{company_type_member}/"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_csv = f'{output_dir}/{company_type_member}_http_raw.csv'

# Reading
log_root_dir = f'/data2/visitor/ASE25/Chimera-Dataset/'

id_role_map = {}
id_list = []
profile_list = []

#######################
profile_output_dir = f"{root_dir}/experiment_output/{foundation_model}_{company_type_member}/generated_members"
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

for week in weeks:
    weekly_dir = os.path.join(log_root_dir, scenario, f'week{week}-{foundation_model}-{company_type}')
    execution_log_path = os.path.join(weekly_dir, "execution_logs")
    
    for member_id in tqdm(id_list, desc=f"Processing member logs for week {week}", leave=False):    
        user_log_dir = os.path.join(execution_log_path, member_id)

        # for every file inside the user_log_dir, read the file and extract the content and do not read the file with "solution"
        log_files = [f for f in os.listdir(user_log_dir) if f.endswith('.log') and 'solution' not in f]
        for member_action_log in tqdm(log_files, desc=f"Processing logs for {member_id}", leave=False):
            member_action_log_path = os.path.join(user_log_dir, member_action_log)

            with open(member_action_log_path, 'r') as f:
                content = f.readlines()
            for line in content:
                if "'function': {'name':" in line:
                    match = re.search(r"'name': '([^']+)'", line)
                    if match:
                        function_name = match.group(1)
                        # extract the time
                        time = line.split(',')[0].strip()
                        
                        # clean_line = line.encode('utf-8').decode('unicode_escape')
                        # get the urls for accessing the function
                        urls = re.findall(r'https?://[^\s]+', line)
                        # deduplicate urls
                        urls = list(set(urls))
                        # print(urls)
                        # assert False
                        for url in urls:
                            # if url contains '}, remove i
                            url = url.split("\'}")[0]
                            url = url.split("\')")[0]
                            url = url.split("]")[0]
                            url = clean_url(url)
                            
                            row = {
                                'real_timestamp': time,
                                'id': member_id,
                                'url': url
                            }
                        # if row url is not equal to the previous row url, append the row
                        if url != last_url:
                            data_rows.append(row)
                            last_url = url

df = pd.DataFrame(data_rows)
# sort by real_timestamp before saving
df['real_timestamp'] = pd.to_datetime(df['real_timestamp'], format='%Y-%m-%d %H:%M:%S')
df = df.sort_values(by='real_timestamp', ascending=True).reset_index(drop=True)

# check whether previous url is same as current url
dupe_mask = (df['url'] == df['url'].shift(1)) & (df['id'] == df['id'].shift(1))
df = df[~dupe_mask].reset_index(drop=True)

df.to_csv(output_csv, index=False, encoding='utf-8') # save the raw

# Processing the raw

raw_csv = f'{output_dir}/{company_type_member}_http_raw.csv'

# reading the raw csv
raw_df = pd.read_csv(raw_csv, encoding='utf-8')

# 1. match up with the actual time
logon_csv = f'{output_dir}/{company_type_member}_logon_full.csv'
logon_df = pd.read_csv(logon_csv, encoding='utf-8')

logon_df['real_timestamp'] = pd.to_datetime(logon_df['real_timestamp'])
logon_df['date'] = pd.to_datetime(logon_df['date'])
raw_df['real_timestamp'] = pd.to_datetime(raw_df['real_timestamp'])

http_dates = []

raw_df = raw_df.sort_values('real_timestamp')
logon_df = logon_df.sort_values('real_timestamp')

result = pd.merge_asof(
    raw_df,
    logon_df,
    on='real_timestamp',
    by='id',
    direction='nearest'
)

# 2. mutate the date time by up to 1 minute

result['date'] = result['date'].apply(mutate_time)

# 3. remove sim_timestamp, real_timestamp, activity
result.drop(columns=['sim_timestamp', 'real_timestamp', 'activity'], inplace=True)

# 4. sort by date
result = result.sort_values(by='date', ascending=True).reset_index(drop=True)

# 5. content column
def fetch_content(url):
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return resp.text[:5000]  # Limit content to first 1000 characters
    except Exception as e:
        return f"Error: {e}"
tqdm.pandas()
result['content'] = result['url'].progress_apply(fetch_content)

# 6. save the result
output_csv = f'{output_dir}/{company_type}_http.csv'
# result.to_csv(output_csv, index=False, encoding='utf-8')
result.to_csv(
    output_csv, 
    index=False, 
    encoding='utf-8',
    escapechar='\\'
)