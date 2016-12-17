from collections import defaultdict
import json
from datetime import datetime, timedelta
import re
import pandas as pd
import pickle
from keras.preprocessing import sequence
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Embedding
from keras.layers import LSTM, SimpleRNN, GRU


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
                date_object = datetime.strptime(time_element[:-6], '%Y-%m-%dT%H:%M:%S.%f')
            else:
                date_object = datetime.strptime(time_element[:-6], '%Y-%m-%dT%H:%M:%S')
            all_data_paired_with_time.append((line, date_object))
    print('sorting by time ...')
    s = sorted(all_data_paired_with_time, key=lambda p: p[1])
    to_output = [pair[0] for pair in s]
    print("dumping json to",output_name)
    with open(output_name, mode='w') as f:
        for line in to_output:
            f.write(line)
    return output_name


def parse_event(data):
    """data is a dict, returns a string"""
    event_type = data['event_type']
    # BerkeleyX/Stat_2\.1x/1t2014
    if re.match(r"/courses/[^/]+/[^/]+/[^/]+/courseware/", event_type):
        parsed_event = 'courseware_load'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/jump_to_id/[^/]+/?$", event_type):
        parsed_event = "jump_to_id"
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/$", event_type):
        parsed_event = 'homepage'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/users$", event_type):
        parsed_event = 'view users'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/about$", event_type):
        parsed_event = 'about page'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/course_wiki$", event_type):
        parsed_event = 'wiki homepage'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/forum/?$", event_type):
        parsed_event = "forum homepage"
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/info/$", event_type):
        parsed_event = "course info"
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/[^/]+/threads/create$", event_type):
        parsed_event = 'create discussion'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/comments/[^/]+/reply$", event_type):
        parsed_event = 'reply discussion comment'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/comments/[^/]+/flagAbuse$", event_type):
        parsed_event = 'flag abuse discussion comment'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/comments/[^/]+/unFlagAbuse$", event_type):
        parsed_event = 'unflag abuse discussion comment'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/comments/[^/]+/delete$", event_type):
        parsed_event = 'delete discussion comment'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/comments/[^/]+/upvote$", event_type):
        parsed_event = 'upvote discussion comment'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/comments/[^/]+/update$", event_type):
        parsed_event = 'update discussion comment'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/comments/[^/]+/unvote$", event_type):
        parsed_event = 'unvote discussion comment'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/comments/[^/]+/endorse$", event_type):
        parsed_event = 'endorse discussion comment'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/comments/[^/]+$", event_type):
        parsed_event = 'load discussion comment'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/forum/[^/]+/inline$", event_type):
        parsed_event = 'inline discussion'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/forum/[^/]+/threads/[^/]+", event_type):
        parsed_event = 'thread discussion'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/[^/]+/threads/create$", event_type):
        parsed_event = 'create thread discussion'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/threads/[^/]+/threads/follow$", event_type):
        parsed_event = 'follow thread2 discussion'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/threads/[^/]+/threads/unfollow$", event_type):
        parsed_event = 'unfollow thread2 discussion'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/threads/[^/]+/threads/reply$", event_type):
        parsed_event = 'reply thread2 discussion'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/threads/[^/]+/threads/upvote$", event_type):
        parsed_event = 'upvote thread2 discussion'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/threads/[^/]+/threads/unvote$", event_type):
        parsed_event = 'unvote thread2 discussion'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/threads/[^/]+/threads/delete$", event_type):
        parsed_event = 'delete thread2 discussion'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/threads/[^/]+/follow$", event_type):
        parsed_event = 'follow thread discussion'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/threads/[^/]+/unfollow$", event_type):
        parsed_event = 'unfollow thread discussion'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/threads/[^/]+/reply$", event_type):
        parsed_event = 'reply thread discussion'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/threads/[^/]+/upvote$", event_type):
        parsed_event = 'upvote thread discussion'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/threads/[^/]+/unvote$", event_type):
        parsed_event = 'unvote thread discussion'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/threads/[^/]+/delete$", event_type):
        parsed_event = 'delete thread discussion'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/threads/[^/]+/update$", event_type):
        parsed_event = 'update thread discussion'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/threads/[^/]+/pin$", event_type):
        parsed_event = 'pin thread discussion'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/threads/[^/]+/unpin$", event_type):
        parsed_event = 'unpin thread discussion'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/threads/[^/]+/flagAbuse$", event_type):
        parsed_event = 'flag abuse thread discussion'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/threads/[^/]+/unFlagAbuse$", event_type):
        parsed_event = 'delete thread discussion'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/discussion/upload", event_type):
        parsed_event = 'upload to discussion'
    elif re.match(r'/courses/[^/]+/[^/]+/[^/]+/info', event_type):
        parsed_event = 'info page'
    elif re.match(r'/courses/[^/]+/[^/]+/[^/]+/progress', event_type):
        parsed_event = 'progress page'
    elif re.match(r"/courses/[^/]+/[^/]+/[^/]+/wiki/.*", event_type):
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
    """log_file is path to event log
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
                date_object = datetime.strptime(time_element[:-6], '%Y-%m-%dT%H:%M:%S.%f')
            else:
                date_object = datetime.strptime(time_element[:-6], '%Y-%m-%dT%H:%M:%S')
            # Get only data up to set date, and only if student had an event in the first wee
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


if __name__ == "__main__":
    course_list = [
        ("../ORDERED_DelftX_AE1110x_1T2014.log",
            "../../data/DelftX-AE1110x-1T2014-certificates_generatedcertificate-prod-analytics.sql",
            "../../data/DelftX-AE1110x-1T2014-auth_user-prod-analytics.sql",
            datetime(2014, 2, 24, 0, 30, 0, 0)),
        ("../ORDERED_BerkeleyX_Stat_2.1x_1T2014-events.log",
            "../../data/BerkeleyX-Stat_2.1x-1T2014-certificates_generatedcertificate-prod-analytics.sql",
            "../../data/BerkeleyX-Stat_2.1x-1T2014-auth_user-prod-analytics.sql",
            datetime(2014, 2, 23, 23, 0, 0, 0)),
        # ("../ORDERED_DelftX_AE1110x_2T2015-events.log",
        #     "../../data/DelftX-AE1110x-2T2015-certificates_generatedcertificate-prod-analytics.sql",
        #     "../../data/DelftX-AE1110x-2T2015-auth_user-prod-analytics.sql",
        #     datetime(2015, 6, 2, 16, 0, 0, 0)),
        ("../ORDERED_DelftX_EX101x_1T2015.log",
            "../../data/DelftX-EX101x-1T2015-certificates_generatedcertificate-prod-analytics.sql",
            "../../data/DelftX-EX101x-1T2015-auth_user-prod-analytics.sql",
            datetime(2015, 3, 31, 8, 0, 0, 0))
        # ("../ORDERED_DelftX_EX101x_3T2015.log",
        #     "../../data/DelftX-EX101x-3T2015-certificates_generatedcertificate-prod-analytics.sql",
        #     "../../data/DelftX-EX101x-3T2015-auth_user-prod-analytics.sql",
        #     datetime(2015, 8, 31, 8, 0, 0, 0))
        ]
    all_list = {}
    for week_num in range(1, 6):
        for course in course_list:
                [x_all, y_all, username_full] = get_events_for_week(course[0], course[1], course[2], week_num, course[3])
                all_list[course[0]] = {'x_full': x_all, 'y_full': y_all, 'username_full': username_full}
        with open('week_' + str(week_num) + '_data_courses.pickle', 'wb') as f:
            pickle.dump(all_list, f)
        all_list = {}

# At this point, main code moves to run_lstm.py
