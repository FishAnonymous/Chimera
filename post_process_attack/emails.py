import os 
import pandas as pd
import json
import ast

def attack_email(scenario, company_type, company_type_member, log_root_dir, root_dir, attack_log_dir, output_dir):

    dates = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # concat all the email.csv
    email_csvs = pd.DataFrame()

    email_log_path = os.path.join(attack_log_dir, 'email.csv')

    email_csvs = pd.read_csv(email_log_path, encoding='utf-8')

    # update a new column "sim_timestamp" with date and the time. The date start from starting_date and add 1 day when the next cell(time) is smaller than the previous cell
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
    for i in range(len(email_csvs)):
        sim_time = pd.to_datetime(email_csvs.loc[i, 'sim_timestamp'], format='%H:%M:%S')
        email_csvs.loc[i, 'full_sim_timestamp'] = f"{sim_date} {email_csvs.loc[i, 'sim_timestamp']}"

    # Add the missing columns

    ### 1. add id list with content from email_from insert next to the index
    email_csvs.insert(0, 'id', email_csvs['email_from'])

    id_role_map = {}
    id_list = []
    profile_list = []

    profile_output_dir = f"{root_dir}/experiment_output/gemini_{company_type_member}/generated_members"
    for file in os.listdir(profile_output_dir):
        if file.endswith(".jsonc"):
            member_profile_path = os.path.join(profile_output_dir, file)
            with open(member_profile_path, 'r') as f:
                member_profile = json.load(f)
            id_role_map[member_profile['id']] = member_profile['role'] # add id-role map
            id_list.append(member_profile['id'])
            profile_list.append(member_profile) # add profile

    id_email_map = {profile['id']: profile['email'] for profile in profile_list}
    id_pc_map = {profile['id']: profile['container_id'] for profile in profile_list}

    ### 2. replace email_from with the email
    email_csvs['email_from'] = email_csvs['email_from'].map(id_email_map)

    ### 3. replace email_to with the email
    email_csvs['email_to'] = email_csvs['email_to'].map(id_email_map)
    # change the column name to "to"
    email_csvs.rename(columns={'email_to': 'to'}, inplace=True)

    ### 4. replace email_cc list
    for i in range(len(email_csvs)):
        if email_csvs.loc[i, 'email_cc'] == '[]':
            email_cc_out = "NaN"
        else:
            email_cc_list = ast.literal_eval(email_csvs.loc[i, 'email_cc'])
            email_cc_out_list = []
            for email_des in email_cc_list:
                # go through map id_email_map to find the email
                # to lower case
                email_des = email_des.lower()
                email_cc_out_list.append(id_email_map.get(email_des, email_des))
                email_cc_out = ', '.join(email_cc_out_list)
        email_csvs.loc[i, 'email_cc'] = email_cc_out

    ### 5. add new column named "size" to calculate the word count of the email_content
    content_idx = email_csvs.columns.get_loc('content')
    email_csvs.insert(content_idx+1, 'size', email_csvs['content'].apply(lambda x: len(x.split()) if isinstance(x, str) else 0))

    ### 6. add new column named "attachment" with value of "0"
    email_csvs.insert(email_csvs.columns.get_loc('size') + 1, 'attachments', 0)

    ### 7. add new column named "pc" with profile content of "container_id"
    email_csvs.insert(email_csvs.columns.get_loc('name') + 1, 'pc', email_csvs['id'].map(id_pc_map))

    ### 8. add new column named "bcc"
    email_csvs.insert(email_csvs.columns.get_loc('email_cc') + 1, 'bcc', 'NaN')

    sim_idx = email_csvs.columns.get_loc("sim_timestamp")
    full_sim = email_csvs.pop("full_sim_timestamp")
    email_csvs.insert(sim_idx + 1, "full_sim_timestamp", full_sim)

    # rename the column "name" to "user"
    email_csvs.rename(columns={'name': 'user'}, inplace=True)
    # rename the column "full_sim_timestamp" to "time"
    email_csvs.rename(columns={'full_sim_timestamp': 'date'}, inplace=True)
    # rename the column "email_cc" to "cc"
    email_csvs.rename(columns={'email_cc': 'cc'}, inplace=True)
    email_csvs.rename(columns={'email_from': 'from'}, inplace=True)

    # remove the column "real_timestamp" and "sim_timestamp"
    email_csvs.drop(columns=['real_timestamp', 'sim_timestamp'], inplace=True)

    # sorting by time
    email_csvs = email_csvs.sort_values(by='date', ascending=True).reset_index(drop=True)

    # save the email_csvs to csv
    email_csvs.to_csv(f'{output_dir}/{company_type_member}_email.csv', index=False, encoding='utf-8')