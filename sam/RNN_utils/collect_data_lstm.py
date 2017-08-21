from collections import defaultdict
import json
from datetime import timedelta
import datetime
import re
import pandas as pd
import numpy as np
import pickle
import glob
import xml.etree.ElementTree as ET

# Main code is get_all_event_streams_instructor_paced
GENPATH = "./" #course folder should be in this directory
COURSES = ["BerkeleyX-ColWri.3.10-1T2016", "BerkeleyX-CS169.2x-1T2016"] # Used to create attrition labels



def generate_ordered_event_copy(event_log_file_name):
    """
    Takes in an event log file, with one action per row, orders the actions by time, and then writes a new file.
    New file will be placed in current directory.
    ../data/BerkeleyX_Stat_2.1x_1T2014-events.log
    Example: generate_ordered_event_copy("../data/DelftX_AE1110x_1T2014.log")
    """
    output_name = "ORDERED_" + event_log_file_name.split('/')[-1]
    all_data_paired_with_time = []
    with open(event_log_file_name) as data_file:
        for line in data_file.readlines():
            try:
                data = json.loads(line)
            except:
                print(line)
                continue
            time_element = data['time']
            if '.' in time_element:
                date_object = datetime.datetime.strptime(time_element[:-6], '%Y-%m-%dT%H:%M:%S.%f')
            else:
                date_object = datetime.datetime.strptime(time_element[:-6], '%Y-%m-%dT%H:%M:%S')
            all_data_paired_with_time.append((line, date_object))
    print('sorting by time ...')
    s = sorted(all_data_paired_with_time, key=lambda p: p[1])
    to_output = [pair[0] for pair in s]
    print("dumping json to",output_name)
    with open(output_name, mode='w') as f:
        for line in to_output:
            f.write(line)
    return output_name

# Optional utility function to view event frequency
def collect_event_frequency(list_of_course_log_files):
    """gets frequency of event types in log files"""
    event_type_count = defaultdict(int)
    event_course_count = defaultdict(int)
    for log_file in list_of_course_log_files:
        event_course_counted = set()
        print(log_file)
        with open(log_file) as f:
            for line in f:
                try:
                    data = json.loads(line)
                    parsed_event = parse_event(data)
                    event_type_count[parsed_event] += 1
                    # Once for each parsed event in a course, add to number of courses
                    if parsed_event not in event_course_counted:
                        event_course_count[parsed_event] += 1
                        event_course_counted.add(parsed_event)
                except ValueError:
                    print(line)
        with open('progress_event_type_count.pickle', 'wb') as f:
            pickle.dump([event_type_count, event_course_count], f)
    # test = pd.DataFrame([{'event': x[0], 'count': x[1]} for x in event_freq.items()])
    # test = pd.DataFrame([{'event': x[0], 'count': x[1], 'course_count': event_freq_list[1][x[0]]} for x in event_freq_list[0].items()])
    return [event_type_count, event_course_count]


def parse_event(data):
    """data is a dict, returns a string indicating event type"""
    event_type = data['event_type']
    # BerkeleyX/Stat_2\.1x/1t2014
    if re.match(r"/courses/.+/courseware/", event_type):
        parsed_event = 'courseware_load'
    elif re.match(r"/courses/.+/jump_to_id/[^/]+/?$", event_type):
        parsed_event = "jump_to_id"
    elif re.match(r"/courses/.+/$", event_type):
        parsed_event = 'homepage'
    elif re.match(r"/courses/.+/discussion/users$", event_type):
        parsed_event = 'view users'
    elif re.match(r"/courses/.+/about$", event_type):
        parsed_event = 'about page'
    elif re.match(r"/courses/.+/course_wiki$", event_type):
        parsed_event = 'wiki homepage'
    elif re.match(r"/courses/.+/discussion/forum/?$", event_type):
        parsed_event = "forum homepage"
    elif re.match(r"/courses/.+/info/$", event_type):
        parsed_event = "course info"
    elif re.match(r"/courses/.+/discussion/[^/]+/threads/create$", event_type):
        parsed_event = 'create discussion'
    elif re.match(r"/courses/.+/discussion/comments/[^/]+/reply$", event_type):
        parsed_event = 'reply discussion comment'
    elif re.match(r"/courses/.+/discussion/comments/[^/]+/flagAbuse$", event_type):
        parsed_event = 'flag abuse discussion comment'
    elif re.match(r"/courses/.+/discussion/comments/[^/]+/unFlagAbuse$", event_type):
        parsed_event = 'unflag abuse discussion comment'
    elif re.match(r"/courses/.+/discussion/comments/[^/]+/delete$", event_type):
        parsed_event = 'delete discussion comment'
    elif re.match(r"/courses/.+/discussion/comments/[^/]+/upvote$", event_type):
        parsed_event = 'upvote discussion comment'
    elif re.match(r"/courses/.+/discussion/comments/[^/]+/update$", event_type):
        parsed_event = 'update discussion comment'
    elif re.match(r"/courses/.+/discussion/comments/[^/]+/unvote$", event_type):
        parsed_event = 'unvote discussion comment'
    elif re.match(r"/courses/.+/discussion/comments/[^/]+/endorse$", event_type):
        parsed_event = 'endorse discussion comment'
    elif re.match(r"/courses/.+/discussion/comments/[^/]+$", event_type):
        parsed_event = 'load discussion comment'
    elif re.match(r"/courses/.+/discussion/forum/[^/]+/inline$", event_type):
        parsed_event = 'inline discussion'
    elif re.match(r"/courses/.+/discussion/forum/[^/]+/threads/[^/]+", event_type):
        parsed_event = 'thread discussion'
    elif re.match(r"/courses/.+/discussion/[^/]+/threads/create$", event_type):
        parsed_event = 'create thread discussion'
    elif re.match(r"/courses/.+/discussion/threads/[^/]+/threads/follow$", event_type):
        parsed_event = 'follow thread2 discussion'
    elif re.match(r"/courses/.+/discussion/threads/[^/]+/threads/unfollow$", event_type):
        parsed_event = 'unfollow thread2 discussion'
    elif re.match(r"/courses/.+/discussion/threads/[^/]+/threads/reply$", event_type):
        parsed_event = 'reply thread2 discussion'
    elif re.match(r"/courses/.+/discussion/threads/[^/]+/threads/upvote$", event_type):
        parsed_event = 'upvote thread2 discussion'
    elif re.match(r"/courses/.+/discussion/threads/[^/]+/threads/unvote$", event_type):
        parsed_event = 'unvote thread2 discussion'
    elif re.match(r"/courses/.+/discussion/threads/[^/]+/threads/delete$", event_type):
        parsed_event = 'delete thread2 discussion'
    elif re.match(r"/courses/.+/discussion/threads/[^/]+/follow$", event_type):
        parsed_event = 'follow thread discussion'
    elif re.match(r"/courses/.+/discussion/threads/[^/]+/unfollow$", event_type):
        parsed_event = 'unfollow thread discussion'
    elif re.match(r"/courses/.+/discussion/threads/[^/]+/reply$", event_type):
        parsed_event = 'reply thread discussion'
    elif re.match(r"/courses/.+/discussion/threads/[^/]+/upvote$", event_type):
        parsed_event = 'upvote thread discussion'
    elif re.match(r"/courses/.+/discussion/threads/[^/]+/unvote$", event_type):
        parsed_event = 'unvote thread discussion'
    elif re.match(r"/courses/.+/discussion/threads/[^/]+/delete$", event_type):
        parsed_event = 'delete thread discussion'
    elif re.match(r"/courses/.+/discussion/threads/[^/]+/update$", event_type):
        parsed_event = 'update thread discussion'
    elif re.match(r"/courses/.+/discussion/threads/[^/]+/pin$", event_type):
        parsed_event = 'pin thread discussion'
    elif re.match(r"/courses/.+/discussion/threads/[^/]+/unpin$", event_type):
        parsed_event = 'unpin thread discussion'
    elif re.match(r"/courses/.+/discussion/threads/[^/]+/flagAbuse$", event_type):
        parsed_event = 'flag abuse thread discussion'
    elif re.match(r"/courses/.+/discussion/threads/[^/]+/unFlagAbuse$", event_type):
        parsed_event = 'delete thread discussion'
    elif re.match(r"/courses/.+/discussion/threads/[^/]+/close$", event_type):
        parsed_event = 'close thread discussion'
    elif re.match(r"/courses/.+/discussion/upload", event_type):
        parsed_event = 'upload to discussion'
    elif re.match(r'/courses/.+/info', event_type):
        parsed_event = 'info page'
    elif re.match(r'/courses/.+/pdfbook/', event_type):
        parsed_event = 'pdf book'
    elif re.match(r'/courses/.+/progress', event_type):
        parsed_event = 'progress page'
    elif re.match(r"/courses/.+/wiki/.*", event_type):
        parsed_event = 'wiki page'
    else:
        parsed_event = event_type
    # check for correct or incorrect problem_check
    if parsed_event == "problem_check":
        if data["event"]["success"] == "correct":
            parsed_event = 'problem_check_correct'
        else:
            parsed_event = 'problem_check_incorrect'
    return parsed_event


def get_ce_types():
    """gets event types from file, returns a dictionary with integer encodings"""
    with open('RNN_event_list.csv') as f:
        event_list = f.read().splitlines()
    return {etype: i for i, etype in enumerate(event_list)}


def get_events_for_week(log_file, certificate_file, user_file, num_weeks, first_day):  
    """
        parses events into number of certified users, where time slice = 1 week
    log_file is path to event log
    certificate_file is path to certificate list
    num_weeks is number of weeks to collect data for
    first_day is a datetime of the first day
    Example: get_events_for_week("../ORDERED_BerkeleyX_Stat_2.1x_1T2014-events.log", ...)
    """
    print("Starting", log_file)
    total_weeks = 5 # Total weeks for analysis (possible for dropping out)
    # Ex. max_date = datetime(2014, 3, 3, 0, 0, 0, 0)
    max_date = first_day + timedelta(days=7*num_weeks)
    one_week_date = first_day + timedelta(days=7)
    # Learning about event types
    ce_types = get_ce_types()
    event_type_count = defaultdict(int)
    event_stream_per_student = defaultdict(list)
    # Find students with certificates
    cert_df = pd.read_table(certificate_file)
    user_df = pd.read_table(user_file)
    cert_df = cert_df[['user_id', 'status']]
    user_df = user_df[['id', 'username', 'is_staff']]
    cert_df = user_df.merge(cert_df, left_on='id', right_on='user_id', how='left')
    staff_usernames = cert_df['username'][cert_df['is_staff'] == 1].values
    students_passing = cert_df['username'][cert_df['status'] == 'downloadable'].values
    # Get events from log_file
    with open(log_file) as f:
        for line in f:
            data = json.loads(line)
            parsed_event = parse_event(data)
            event_type_count[parsed_event] += 1
            # Get last event time
            time_element = data['time']
            username = data['username']
            if '.' in time_element:
                date_object = datetime.datetime.strptime(time_element[:-6], '%Y-%m-%dT%H:%M:%S.%f')
            else:
                date_object = datetime.datetime.strptime(time_element[:-6], '%Y-%m-%dT%H:%M:%S')
            # Get only data up to set date, and only if student had an event in the first week
            if date_object < max_date and parsed_event in ce_types:
                if username in event_stream_per_student or date_object < one_week_date:
                    event_stream_per_student[username].append(ce_types[parsed_event])
            # leave loop if past end date
            if date_object > max_date:
                break
    print("Total number of student with certification is " + str(len(students_passing)))
    print("Total students is " + str((cert_df['is_staff'] == 0).sum()))
    print("Total users with events is " + str(len(event_stream_per_student)))

    # For each student who has at least signed up for the class
    # by x weeks in, add an entry to both the x_full and y_full list
    x_full = []
    y_full = []
    username_full = []
    for student, event_stream in event_stream_per_student.items():
        if student not in staff_usernames:
            x_full.append(event_stream)
            username_full.append(student)
            if student in students_passing:
                y_full.append(0)  # did not drop out
            else:
                y_full.append(1)  # did drop out

    return [x_full, y_full, username_full]


def simple_count(filename):
    """get number of lines in file"""
    lines = 0
    for line in open(filename):
        lines += 1
    return lines


def get_events_df(log_file, certificate_file, user_file):
    """
    parses events into number of certified users, no time considerations
    log_file is path to event log
    certificate_file is path to certificate list
    num_weeks is number of weeks to collect data for
    first_day is a datetime of the first day
    Example: get_events_df("../ORDERED_BerkeleyX_Stat_2.1x_1T2014-events.log", ...)
    """
    print("Starting", log_file)
    print(datetime.datetime.now())
    date_list = []
    username_list = []
    event_list = []
    # Ex. max_date = datetime(2014, 3, 3, 0, 0, 0, 0)
    # Learning about event types
    ce_types = get_ce_types()
    # Find students with certificates
    cert_df = pd.read_table(certificate_file)
    user_df = pd.read_table(user_file)
    cert_df = cert_df[['user_id', 'status']]
    user_df = user_df[['id', 'username', 'is_staff']]
    cert_df = user_df.merge(cert_df, left_on='id', right_on='user_id', how='left')
    students = set((cert_df['username'][cert_df['is_staff'] == 0]).values)
    # Get events from log_file
    with open(log_file) as f:
        for line in f:
            try:
                data = json.loads(line)
            except ValueError:
                print(line)
                continue
            parsed_event = parse_event(data)
            # Get event time
            time_element = data['time']
            username = data['username']
            if '.' in time_element:
                date_object = datetime.datetime.strptime(time_element[:-6], '%Y-%m-%dT%H:%M:%S.%f')
            else:
                date_object = datetime.datetime.strptime(time_element[:-6], '%Y-%m-%dT%H:%M:%S')
            if parsed_event in ce_types and username in students:
                username_list.append(username)
                event_list.append(ce_types[parsed_event])
                date_list.append(date_object)
    events_df = pd.DataFrame({'username': username_list, 'event': event_list, 'date': date_list})
    print("Total students is " + str((cert_df['is_staff'] == 0).sum()))
    return events_df

def get_events_from_folder_name_generic(name, home_path, target_path):
    print(datetime.datetime.now())
    log_file = home_path + name.replace("-", "_") + '-event.log'
    certificate_file = home_path + name + '-certificates_generatedcertificate-prod-analytics.sql'
    user_file = home_path + name + '-auth_user-prod-analytics.sql'
    log_df = get_events_df(log_file, certificate_file, user_file)
    print(datetime.datetime.now())
	# target_path and home_path should end in /
    with open(target_path + name + '.pickle', 'wb') as f:
        pickle.dump(log_df, f)
    print(datetime.datetime.now())


def get_all_event_streams():
    return pd.concat([get_all_event_streams_instructor_paced(), get_all_event_streams_self_paced()])


def get_all_event_streams_instructor_paced(home_path):
    course_df = pd.read_csv('course_summary.csv')
    course_list = (course_df['course'][(course_df['certified'] > 100) & (course_df['instructor_paced'] == 1)]).values
    outlier_cutoff_list = [get_event_streams_train(x, home_path) for x in course_list]
    outlier_cutoff_list_test = [get_event_streams_test(x, home_path) for x in course_list]
    outlier_df = pd.DataFrame({'course': course_list, 'outlier_cutoff': outlier_cutoff_list})
    outlier_df.to_csv('self_paced_outlier_list.csv')
    return outlier_df


def get_all_event_streams_self_paced(home_path):
    course_df = pd.read_csv('course_summary.csv')
    course_list = (course_df['course'][(course_df['certified'] > 100) & (course_df['instructor_paced'] == 0)]).values
    outlier_cutoff_list = [get_event_streams_train(x) for x in course_list]
    outlier_cutoff_list_test = [get_event_streams_test(x, home_path) for x in course_list]
    outlier_df = pd.DataFrame({'course': course_list, 'outlier_cutoff': outlier_cutoff_list})
    outlier_df.to_csv('instructor_paced_outlier_list.csv')
    return outlier_df

# Time sliced in weeks
def get_event_streams_train(course_name, home_path):
	"""
    reads course_summary.csv for course start and end date 
    home_path is path where course sql files are contained
    returns certification information for course users
    """
    print(course_name)
    course_df = pd.read_csv('course_summary.csv')
    this_course_df = course_df[course_df['course'] == course_name]
    start_date = datetime.datetime.strptime(this_course_df['start_date'].values[0], '%m/%d/%y %H:%M')  # Format from Excel
    end_date = datetime.datetime.strptime(this_course_df['end_date'].values[0], '%m/%d/%y %H:%M')
    last_week = int((end_date - start_date).days / 7)
    with open('course_events/' + course_name + '.pickle', 'rb') as f:
        log_df = pickle.load(f)
    # Drop events after end of course
    log_df = log_df[log_df['date'] < end_date]
    log_df.sort_values(by='date', inplace=True)
    log_df['week'] = (log_df['date'] - start_date).dt.days / 7
    u_group = log_df.groupby('username')
    usernames = []
    u_seqs = []
    # convert instructor paced to self-paced
    self_paced = this_course_df['instructor_paced'].iloc[0] == 0
    if self_paced:
        log_df['event_offset'] = log_df['event'] + 1  # leave 1 for 0 fill-in
    else:
        log_df['event_offset'] = log_df['event'] + 11  # leave 10 for week endings
    for username, group in u_group:
        if self_paced:
            u_seq = group['event_offset'].values
            usernames.append(username)
            u_seqs.append(u_seq)
        else:
            # Get up to end of first week
            u_seq = (group['event_offset'][group['week'] < 1]).tolist()
            # Only include users who took some action in the first week
            if len(u_seq) > 0:
                u_seq.append(1)  # end of week 1
                # Get all weeks, up to a max of 10
                for i in range(1, min(last_week, 10)):
                    u_seq.extend((group['event_offset'][(group['week'] >= i) & (group['week'] < i + 1)]).tolist())
                    u_seq.append(i + 1)
                # Add all events past end of last week
                u_seq.extend(
                    (group['event_offset'][(group['week'] >= last_week) & (group['date'] < end_date)]).tolist())
                usernames.append(username)
                u_seqs.append(u_seq)
    user_df = pd.DataFrame({'username': usernames, 'seq': u_seqs})
    v_len = np.vectorize(len)
    user_df['seq_len'] = v_len(user_df['seq'])
    cert_file = home_path + course_name + "-certificates_generatedcertificate-prod-analytics.sql"
    user_file = home_path + course_name + "-auth_user-prod-analytics.sql"
    cert_df = pd.read_table(cert_file)
    user_list_df = pd.read_table(user_file)
    cert_df = cert_df[['user_id', 'status']]
    user_list_df = user_list_df[['id', 'username', 'is_staff']]
    cert_df = user_list_df.merge(cert_df, left_on='id', right_on='user_id', how='left')
    cert_df = cert_df[['username', 'status', 'is_staff']]
    user_df = user_df.merge(cert_df, on='username')
    certificate_users = user_df[user_df['status'] == 'downloadable']
    q1 = np.percentile(certificate_users['seq_len'], 25)
    q3 = np.percentile(certificate_users['seq_len'], 75)
    outlier_cutoff = q3 + 1.5 * (q3 - q1)
    print("25%", np.percentile(certificate_users['seq_len'], 25))
    print("75%", np.percentile(certificate_users['seq_len'], 75))
    print('outlier cutoff:', outlier_cutoff)
    users_to_keep = user_df[(user_df['seq_len'] < outlier_cutoff) & (user_df['status'] == 'downloadable')]
    user_no_certificate = user_df[(user_df['seq_len'] < outlier_cutoff) & (user_df['status'] != 'downloadable')]
    user_no_cert_keep = user_no_certificate.sample(len(users_to_keep) * 2)
    users_keep = pd.concat([users_to_keep, user_no_cert_keep])
    #     add code to have auto-creation of folders
    with open('course_users/' + course_name + '_users.pickle', 'wb') as f:
        pickle.dump(users_keep, f)
    return outlier_cutoff


def get_all_event_stream_test():
    course_df = pd.read_csv('instructor_paced_fold_list.csv')
    for course in course_df['course']:
        get_event_streams_test(course)


def get_event_streams_test(course_name, home_path):
    """
    reads course_summary.csv for course start and end date 
    home_path is path where course sql files are contained
	Gets full event stream for testing model
    """
    print(course_name)
    course_df = pd.read_csv('course_summary.csv')
    this_course_df = course_df[course_df['course'] == course_name]
    start_date = datetime.datetime.strptime(this_course_df['start_date'].values[0], '%m/%d/%y %H:%M')  # Format from Excel
    end_date = datetime.datetime.strptime(this_course_df['end_date'].values[0], '%m/%d/%y %H:%M')
    last_week = int((end_date - start_date).days / 7)
    with open('course_events/' + course_name + '.pickle', 'rb') as f:
        log_df = pickle.load(f)
    # Drop events after end of course
    log_df = log_df[log_df['date'] < end_date]
    log_df.sort_values(by='date', inplace=True)
    log_df['week'] = (log_df['date'] - start_date).dt.days / 7
    u_group = log_df.groupby('username')
    usernames = []
    u_seqs = []
    weeks = []  # number of weeks included in each u_seq
    # convert instructor paced to self-paced
    self_paced = this_course_df['instructor_paced'].iloc[0] == 0
    if self_paced:
        log_df['event_offset'] = log_df['event'] + 1  # leave 1 for 0 fill-in
    else:
        log_df['event_offset'] = log_df['event'] + 11  # leave 10 for week endings
    for username, group in u_group:
        if self_paced:
            # Need personal week for each username
            raise NotImplementedError('need to decide how to split weeks for self-paced')
        else:
            # Get up to end of first week
            u_seq = (group['event_offset'][group['week'] < 1]).tolist()
            # Only include users who took some action in the first week
            if len(u_seq) > 0:
                u_seq.append(1)  # end of week 1
                usernames.append(username)
                weeks.append(1)
                u_seqs.append(list(u_seq))  # append a copy of u_seq
                # Get all weeks, up to a max of 10
                for i in range(1, min(last_week, 10)):
                    u_seq.extend((group['event_offset'][(group['week'] >= i) & (group['week'] < i + 1)]).tolist())
                    u_seq.append(i + 1)
                    usernames.append(username)
                    weeks.append(i + 1)
                    u_seqs.append(list(u_seq))
                # Not adding events after last week
    user_df = pd.DataFrame({'username': usernames, 'seq': u_seqs, 'week': weeks})
    v_len = np.vectorize(len)
    user_df['seq_len'] = v_len(user_df['seq'])
    cert_file = home_path + course_name + "-certificates_generatedcertificate-prod-analytics.sql"
    user_file = home_path + course_name + "-auth_user-prod-analytics.sql"
    cert_df = pd.read_table(cert_file)
    user_list_df = pd.read_table(user_file)
    cert_df = cert_df[['user_id', 'status']]
    user_list_df = user_list_df[['id', 'username', 'is_staff']]
    cert_df = user_list_df.merge(cert_df, left_on='id', right_on='user_id', how='left')
    cert_df = cert_df[['username', 'status', 'is_staff']]
    user_df = user_df.merge(cert_df, on='username')
    with open('course_users/' + course_name + '_users_full.pickle', 'wb') as f:
        pickle.dump(user_df, f)
    return user_df

def attritionLabels():
	"""
    Generates attrition label for course in global COURSES array.
    """
	for course in COURSES:
		print (course)
		for_file_lookup_coursename = course.replace('-','_')
		ordered_course_file_log = 'ORDERED_'+for_file_lookup_coursename+'-event.log' 
		with open(ordered_course_file_log) as f:
			ordered_event_list = f.readlines()
		#student actions, ordered by time
		student_actions = stusort(ordered_event_list)
		no_of_students = len(student_actions)
		#course start and end date
		course_dates = coursedates(course) #returns start, end, no of weeks
		start_date = course_dates[0]
		end_date = course_dates[1]
		num_weeks = course_dates[2]
		student_labels = [] 
		i = 0
		for student in student_actions:
			last_action_index = len(student_actions[student])-1
			last_action_time_messy = student_actions[student][last_action_index]['time'].split('+')[0]
			last_action_time_clean = datetime.datetime.strptime(last_action_time_messy, '%Y-%m-%dT%H:%M:%S.%f' if '.' in last_action_time_messy else '%Y-%m-%dT%H:%M:%S')
			if last_action_time_clean.date() > end_date.date():
				labels = [0]*7000
			elif last_action_time_clean.date() < start_date.date():
				labels = [1]*7000 # max sequence length is 7000
			else: 
				two_days_before = last_action_time_clean - timedelta(days=2)
				labels = [0]*7000
				index = 0
				for action in student_actions[student]:
					messy_event_time = action['time'].split('+')[0]
					clean_event_type = datetime.datetime.strptime(messy_event_time, '%Y-%m-%dT%H:%M:%S.%f' if '.' in messy_event_time else '%Y-%m-%dT%H:%M:%S')
					if clean_event_type > two_days_before:
						for num in range(index, 7000):
							labels[num] = 1
						break						
					else:
						index +=1
			student_labels.append([student, labels])
		#splitting data 80:20 into train and test
		train = student_labels[:int(round(len(student_labels)*0.8))]
		test = student_labels[int(round(len(student_labels)*0.8)):]
		with open('course_attr/' + course + '_train_users.pickle', 'wb') as f:
			pickle.dump(train, f)
		with open('course_attr/' + course + '_test_users.pickle', 'wb') as f:
			pickle.dump(test, f)
		with open('course_attr/' + course + '_full_users.pickle', 'wb') as f:
			pickle.dump(student_labels, f)
	return len(student_labels)
	
def stusort(timedat):
    '''Group time-sorted data by student:
       returned: {'stuX':[dict_time0, dict_time3, dict_time4],
                  'stuY':[dict_time1, dict_time2], ...}
       Note that events in returned dict are aggregated across weeks, within:
       [course_start, uppertimelim], across all students in dictionary.
    '''
    # make the dict:
    studat = {}
    for i in timedat:
        i = json.loads(i)
        # limit by week:
        messytime = i['time'].split('+')[0]
        cleantime = datetime.datetime.strptime(messytime, '%Y-%m-%dT%H:%M:%S.%f' if '.' in messytime else '%Y-%m-%dT%H:%M:%S')
        # # If we don't want aggregated data... (each week includes only that week)
        # NOTE: update function inputs to use this
        # if cleantime < timelimit_start:
        #     # not at desired week yet, keep going
        #     # (ensures recorded data is not aggregated across different weeks)
        #     continue
#         if cleantime > uppertimelim:
            # gone too far, break out of loop
#             break
        # if we've made it this far, we're in the right week! record:
        tmp_id = i['username']
        # if that student has already been added:
        if tmp_id in studat:
            studat[tmp_id].append(i)
        # otherwise... create a new one!
        else:
            studat[tmp_id] = [i]
    return studat

def coursedates(course):
    '''Look in all course folders for start and end dates;
        return one dictionary of the form...
        datedict = {'course_A': [start_time, end_time, num_weeks],
                    'course_B': [start_time, end_time, num_weeks],
                    ...}
    '''
    # naming varies, but always only one xml file in this folder
    xml_name = glob.glob(GENPATH + course + "/course/*.xml")[0]
    tree = ET.parse(xml_name)
    root = tree.getroot()
    tmp_start = root.attrib['start'].split("+")[0].strip("Z").strip("\"").strip("\'")
    tmp_end = root.attrib['end'].split("+")[0].strip("Z").strip("\"").strip("\'")
    # and now convert times into datetime objects:
    new_start = datetime.datetime.strptime(tmp_start, '%Y-%m-%dT%H:%M:%S.%f' if '.' in tmp_start else '%Y-%m-%dT%H:%M:%S')
    new_end = datetime.datetime.strptime(tmp_end, '%Y-%m-%dT%H:%M:%S.%f' if '.' in tmp_end else '%Y-%m-%dT%H:%M:%S')
    # and compute number of weeks between start and end:
    num_weeks = round((new_end - new_start).total_seconds()/604800)  # 604800: number of seconds in one week
    # now append course and info to dictionary:
    return [new_start, new_end, num_weeks]
