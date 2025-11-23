# TODO

## Features

Everyone store array (todo list) and a writable working table (real_schedule.out)
todo list: [starting time, todo stuff] (loop per second check)
Status: Working / Idle
Idle + communication -> update todo list -> recall 
Schedule(list+goal): exec container, run owl -> get todo list
Execute(task): exec container, run owl -> get result

- [x] Meeting design - workforce - to log the result and the procedures during the meeting (in camel)
- [x] Finish export OPENAI KEY into env
- [x] log all logs of agent into destinated location - insufficient
- [x] construct_society should be optimized with full capability

- [x] Automated Meeting Script (follow the number of employee in the company)
    - fixed.py -> auto.py
- [x] containerization for each user (Pri)
- [] Attack explore
- [x] Log Collection - Matching CERT
  - [x] Logon
  - [x] Email
  - [x] LDAP
  - [x] URL
  - [-] Device (Perhaps container login?)
  - [x] Personality (To be update)
- [x] host local email (might not be needed)

## Daily Activity
1. Meeting for weekly task goal for each member (save meeting minute, workforce)
2. Everyday plan for each member (save to init_plan/member_day.csv), check result, if not format alike, raise error
3. simulate, take one second as 60, execute. if not finish, then pospone and reschedule, if new message arrive, then reschedule. contact need to write email.
4. loafing, personal interest, accept new message in email.

## NEXT
- [x] update five users backgound with better personality features
- [x] email feature
  - [x] email members
  - [x] email content
  - [x] reply email and whether to terminate
- [x] smooth update schedule
- [x] update schedule and reply email not instantly
- [x] fix the email logging content containing \n in parsing
- [x] log all the behaviors
- [x] record the email communication and update the execution logging
- [x] email send and reply email should be wrapped into Process
- [x] check email logging and terminal daemon logging whether correct in testing
- [x] random browsing when free
- [-] add observatry daemon when executing (not helpful)

- [x] achieve fully automation
  - [x] serial automation with README document
  - [x] refine the personal metrics (human study)
  - [x] workforce meeting automation
  - [x] post meeting analysis for weekly plan for each member
  - [x] automation for daily plan generation
  - [x] serial the weekly execution
  - [x] fix email automation for each specific member (Urgent) (Better check with all)
  - [] background execution on Ubuntu server
  - [x] add start to work feature
  - [-] two days execution including weekends
- [x] find the earliest time to start a day and then record

- [x] log collection
  - [x] log all the time (current_time and real_time)
  - [x] containerization for log collection
  - [x] traffic collection

- [x] attack
  - [x] administrative attack 
  - [x] exploit attack

- [-] summarize featrue for one day's execution

## Robustness
- [x] add max attempt time to ensure every json file parsing is correct
- [x] test with accelerated timing
- [x] more user incorporated

## Debugging
- [x] error messages and warning for each attempt
- [x] bug double info in completed all task reminder
- [x] errored json parsing

## Priority
1. finish one member one day procedure
2. containerization
3. log collection testing
4. multiple user with communication aware for many days

## Timing
current record the real time instead of the simulated time
afterwards, all time will be converted into the simulation time with scaled timing