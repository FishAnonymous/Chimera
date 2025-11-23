# Chimera Anonymous Codespace

## Normal Log Collection

1. Member(Role) Information
2. General Meeting for Individual Task
3. Operate Task (Update Works)
4. Attack

## Procedures

- Configuration
- meeting_for_weekly_goal_fixed.py
    - output/meeting_result.log (response from multi-agent)
    - output/meeting_result.csv (communication via each role during the meeting) - modification in CAMEL/single_agent_worker.py
    - output/meeting_detailed_actions.log (actions during the agent communications)
- post_meeting_summary_fixed.py
    - output/meeting_schedule.json (weekly goal for each member)
- daily_plan_generation.py
    - init_schedule/$ROLE_W$WEEK.json
- user schedule update

## Automated Process

0. (TBD) automatic generation of team.json 
1. Prepare `team.json` and then execute `python profile_generation.py` -> config.profile_output_dir
2. meeting for settle task for each member `python meeting_for_weekly_goal_auto.py` -> config.meeting_log_dir (Note in Camel Setting, the logging for workforce is static required change!)
3. post meeting summary for detailed initial schedule `python post_meeting_summary_auto.py` -> config.meeting_log_dir
4. daily schedule generation for all members for each day `python daily_plan_generation_auto.py` -> initial_schedule
5. daily execution for each day `python daily_execution_auto.py` -> execution_logs

## Dependencies and Custimized Owl/Camel

### Dependency

pip install -r requirements.txt

### Owl

version: commit b7d3e85a704266fda8507cf801cf965713ca4f8
official version: commit 496f78564f95a6e6a503f585fc4cd41f9c2fe258

pip install -e .
pip install -r requirements.txt --use-pep517

### Camel

version: commit 45c17ebbf068f5c54c4657212831f7a8d2e0db4a
official version: commit 8474e26dcf9a2a10e9d2c7504b506f8f8580e4e6

pip install -e ".[all]" 
pip install pre-commit mypy
pre-commit install

## Progress

in [TODO.md](./TODO.md)

## Clean up
rm -rf demo/execution_logs demo/generated_members demo/init_schedule demo/init_schedule_old demo/logs demo/meeting_logs/

---

## Containerization
### Env Setup
```bash
sudo docker run --privileged -it \
  --name chimera \
  -v $LOCAL_DIR:/data \
  --network host \
  ubuntu:22.04 \
  /bin/bash
```

```bash
apt update && apt upgrade
apt install build-essential git vim python3-pip tmux chromium-browser python3-tk iproute2

pip install uv
uv venv .venv --python=3.10
source .venv/bin/activate

# owl
cd owl/
uv pip install -e .

# camel
uv pip install -e ".[all]"
uv pip install -e .
uv pip install pre-commit mypy
# git config --global --add safe.directory /data/Chimera/camel
pre-commit install

# google
uv pip install -U google-genai

# general
uv pip install json5 playwright
playwright install-deps
playwright install
```

### Execution

```bash
source .venv/bin/activate
```

### Log Collection

```bash
### pcap collection
docker inspect -f '{{.State.Pid}}' chimera
nsenter -t $PID -n tcpdump -i any -w /tmp/chimera.pcap
### scap collection
sudo sysdig -v -b -p "%evt.rawtime %user.uid %proc.pid %proc.name %thread.tid %syscall.type %evt.dir %evt.args" -w $OUTPUT_DIR/$FILE_NUMBER.scap container.id=$CONTAINER_ID
```

## Attacks

### Attacker List
* Tech Company
    - cdev-1
    - sdes-1
    - qtest-1

* Finance Corporation
    - qres-1
    - sdev-1
    - facc-1

* Medical Institution
    - his-1
    - rn-1
    - ehrv-1
