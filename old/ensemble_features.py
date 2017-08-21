# MLE - Fall 2016 final project
# defining features for ensebling method

import numpy as np
import json
# import data_processing
import re
import datetime
import math


# Setting list of features to include:
# FEATURES = [2]    # testing
FEATURES = [2, 3, 4, 5, 7, 8, 9, 10, 11, 19]  # all the implemented features
COURSES = ["BerkeleyX-Stat_2.1x-1T2014",
           "DelftX-AE1110x-1T2014",
           "DelftX-AE1110x-2T2015",
           "DelftX-EX101x-1T2015",
           "DelftX-EX101x-3T2015"]


# ================================ PROCESSING DATA =============================
def stusort(timedat, timelimit):
    """Group time-sorted data by student:
       returned: {'stuX':[dict_time0, dict_time3, dict_time4],
                  'stuZ':[dict_time1, dict_time2, dict_time5]}
    """
    # make the dict:
    studat = {}

    for i in timedat:
        i = json.loads(i)

        # limit by week:
        messytime = i['time'][:-6]
        cleantime = datetime.datetime.strptime(messytime, '%Y-%m-%dT%H:%M:%S.%f' if '.' in messytime else '%Y-%m-%dT%H:%M:%S')
        if cleantime > timelimit:
            break

        # otherwise, keep going:
        tmp_id = i['username']

        # if that student has already been added:
        if tmp_id in studat:
            studat[tmp_id].append(i)
        # otherwise... create a new one!
        else:
            studat[tmp_id] = [i]

    return studat


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# NOTE: not building week time limits into feature descriptions; instead, just
# make data input include only desired set of weeks before computing features.
# =========================== ENCODING FEATURES: ===============================
def feat1(studat):
    # NOTE: no longer applicable
    # (testing if they get certificate at end or not; no longer dropout by week)
    """FEATURE: whether the student has stopped out or not
       input: time-sorted data, grouped by student
    """
    pass


def feat2(studat):
    """FEATURE: total time spent on all resources
       input: time-sorted data, grouped by student
    """
    # --------------
    # NOTE: adding up all the time in sessions, except problem events don't have
    # 'sessions', so ignored
    # --------------
    allstu = {}
    for stu in studat:
        # for each student...
        sesh_times = {}
        # {'session1': [start, endtime], 'session2': [start, endtime], etc...}
        for dic in studat[stu]:
            try:
                tmpsesh = dic["session"]
                tmptime = datetime.datetime.strptime(dic["time"][:-6], '%Y-%m-%dT%H:%M:%S.%f' if '.' in dic["time"] else '%Y-%m-%dT%H:%M:%S')
                if tmpsesh in sesh_times:
                    # then initial time is already there, update end time:
                    sesh_times[tmpsesh][1] = tmptime
                else:
                    # then start a new session entry:
                    sesh_times[tmpsesh] = [tmptime, tmptime]
            except KeyError:
                # problem events don't include 'session' number (just ignore):
                continue

        # now take difference of each session and add to total time of student:
        tottime = datetime.timedelta(0)
        for sesh in sesh_times:
            # TODO: make sure time is in proper format to subtract
            tottime += sesh_times[sesh][1] - sesh_times[sesh][0]

        # and add to the allstu dict:
        # TODO: should I normalize time somehow? determine units at least
        allstu[stu] = tottime.total_seconds()

    return allstu


def feat3(studat):
    """FEATURE: number of distinct problems attempted
       input: time-sorted data, grouped by student
    """
    allstu = {}
    for stu in studat:
        num_probs = 0
        for dic in studat[stu]:
            if dic['event_type'] == 'problem_check':
                # then increment number of attempted problems
                # NOTE: this assumes all entries are distinct problems,
                # where multiple problem attempts are collapsed in one entry
                num_probs += 1
        allstu[stu] = num_probs
    return allstu


def feat4(studat):
    """FEATURE: average number of attempts per problem
       input: time-sorted data, grouped by student
    """

    # NOTE: initially stated as "number of submissions (on a problem attempt)"
    # need to change?

    allstu = {}
    for stu in studat:
        attempts = []
        for dic in studat[stu]:
            if dic['event_type'] == 'problem_check':
                attempts.append(dic['event']['attempts'])

        # and set each stu to the average of personal attempts list:
        try:
            allstu[stu] = sum(attempts)/len(attempts)
        # TODO: check that this is the right way to catch the error?
        except ZeroDivisionError:
            allstu[stu] = 0

    # and return results for all students:
    return allstu


def feat5(studat):
    """FEATURE: number of distinct correct problems
       input: time-sorted data, grouped by student
    """
    allstu = {}
    for stu in studat:
        num_correct = 0
        for dic in studat[stu]:
            if dic['event_type'] == 'problem_check':
                if dic['event']['success'] == 'correct':
                    # then increment number of correct problems
                    # NOTE: this assumes all entries are distinct problems,
                    # where multiple problem attempts are collapsed in one entry
                    num_correct += 1
        allstu[stu] = num_correct
    return allstu


def feat6(studat):
    """FEATURE: average number of submissions per problem [x4 / x5]
       input: time-sorted data, grouped by student
    """
    # NOTE: ignore; identical to feature 4 (?)
    pass


def feat7(studat):
    """FEATURE: ratio of total time spent to number of distinct correct problems
       input: time-sorted data, grouped by student
    """
    # NOTE: assuming "total time spent" is time spent on resources overall (f2)
    time_results = feat2(studat)
    prob_results = feat5(studat)

    allstu = {}
    for stu in studat:
        if prob_results[stu] == 0:
            # no correct problems; set to -1 to indicate edge case
            allstu[stu] = -1
        else:
            allstu[stu] = time_results[stu]/prob_results[stu]
    return allstu


def feat8(studat):
    """FEATURE: ratio of number of problems attempted to number of distinct
       correct problems
       input: time-sorted data, grouped by student
    """
    # NOTE: still assuming that each entry is a distinct problem

    allstu = {}
    for stu in studat:
        num_correct = 0
        num_tot = 0
        for dic in studat[stu]:
            if dic['event_type'] == 'problem_check':
                # includes corrects and incorrects
                num_tot += 1
                if dic['event']['success'] == 'correct':
                    # then increment number of correct problems
                    # NOTE: this assumes all entries are distinct problems,
                    # where multiple problem attempts are collapsed in one entry
                    num_correct += 1
        try:
            allstu[stu] = num_correct/num_tot
        except ZeroDivisionError:
            allstu[stu] = 0

    return allstu


def feat9(studat, course):
    """FEATURE: average time difference between submitting a problem and deadline
       input: time-sorted data, grouped by student
    """

    # get deadline data from csv file:
    # f = open("DEADLINES_" + course + ".csv", "r") # use for local machine testing
    f = open("/deepedu/research/moocdrop/code/DEADLINES_" + course + ".csv", "r")

    duedict = {} # keys: problem_ids, values: duedates
    for line in f:
        tmp = line.split(',')
        duedict[tmp[0]] = datetime.datetime.strptime(tmp[1].strip(), '%Y-%m-%dT%H:%M:%S')
    # print(duedict.keys())
    # time between opening a problem and submitting an answer
    # (averaged over all problems, using last submission for each problem)

    allstu = {}         # keys: student_ids, values: student subdict
    for stu in studat:
        submdict = {}    # keys: problem_ids, values: time difference between submission time and due date
        for dic in studat[stu]:
            if dic['event_type'] == 'problem_check':
                # time example - "time": "2014-02-24T06:54:02.113412+00:00"
                messysubmtime = dic['time'][:-6]
                submtime = datetime.datetime.strptime(messysubmtime, '%Y-%m-%dT%H:%M:%S.%f' if '.' in messysubmtime else '%Y-%m-%dT%H:%M:%S')

                # # ASSIGNMENT DEADLINES:
                # # extract problem name from info:
                # coursename = dic['context']['course_id']
                # # but replace "/" with "-" to get correct file name:
                # coursename.replace("/", "-")
                # prob_id = dic['event']['problem_id'].split('/')[-1]
                # # NOTE: make sure I don't need to strip the end of line character from some names? (\)
                # # print(prob_id)
                #
                # # and get appropriate deadline from .xml sequential file:
                # ftmp = open("/deepedu/research/moocdrop/data/" + coursename + "/sequential/" + prob_id, "r")
                #
                # # NOTE: some may have sub-questions... figure that out (that's where the end of line char (\) comes from?)

                # get problem id: ----------------------------------------------
                # USING CORRECT MAPS; not correct, see below
                # long_id = dic['correct_map'].values()[0]
                # # format: <JUNK>-problem-<PROBLEM ID>_x_y (for subparts x,y)
                # long_id_lst = re.split('-|_', long_id)
                #
                # if len(long_id_lst[-1]) == 1: # then that's the subpart:
                #     problem_id = long_id_lst[-3]
                # else: # otherwise no subpart, problem_id is the last thing
                #     problem_id = long_id_lst[-1]

                # TODO: make sure this is the correct format ALWAYS
                # print(dic['event'].keys())
                try:
                    # one case saw 'proble_id'... not worth it
                    problem_id = dic['event']['problem_id'].split('/')[-1]

                    # and get corresponding time difference: -----------------------
                    submdict[problem_id] = [(duedict[problem_id] - submtime).total_seconds()]
                    # TODO: need to normalize the time difference to get cleaner fractions?
                    # NOTE: remember, the larger this difference, the more prepared the student (less likely to drop out?)
                except KeyError:
                    # print("oops")
                    # TODO: not a great solution... missing a lot of problems
                    continue
        allstu[stu] = np.mean(list(submdict.values()))

    return allstu


def feat10(studat):
    """FEATURE: duration of longest observed event (not including problems)
       input: time-sorted data, grouped by student
    """
    # --------------
    # NOTE: considering time in all session types
    # --------------
    allstu = {}
    for stu in studat:
        # for each student...
        sesh_times = {}
        # {'session1': [start, endtime], 'session2': [start, endtime], etc...}
        for dic in studat[stu]:
            try:
                tmpsesh = dic["session"]
                tmptime = datetime.datetime.strptime(dic["time"][:-6], '%Y-%m-%dT%H:%M:%S.%f' if '.' in dic["time"] else '%Y-%m-%dT%H:%M:%S')
                if tmpsesh in sesh_times:
                    # then initial time is already there, update end time:
                    sesh_times[tmpsesh][1] = tmptime
                else:
                    # then start a new session entry:
                    sesh_times[tmpsesh] = [tmptime, tmptime]
            except KeyError:
                # problem events don't have sessions; just ignore
                continue

        # now take difference of each session and add to total time of student:
        maxduration = datetime.timedelta(0)
        for sesh in sesh_times:
            # TODO: make sure time is in proper format to subtract
            tmpduration = sesh_times[sesh][1] - sesh_times[sesh][0]
            if tmpduration > maxduration:
                maxduration = tmpduration
        # and add to the allstu dict:
        # TODO: should I normalize time somehow? determine units at least
        try:
            allstu[stu] = tmpduration.total_seconds()
        except UnboundLocalError:
            # may be empty student? gave error once that tmpduration not yet set
            continue
    return allstu


def feat11(studat):
    """FEATURE: total time spent on lectures (VIDEOS)
       input: time-sorted data, grouped by student
    """
    # --------------
    # NOTE: adding up all the time in video sessions (assuming lectures in video formats only)
    # --------------
    allstu = {}
    for stu in studat:
        # for each student...
        sesh_times = {}
        # {'session1': [start, endtime], 'session2': [start, endtime], etc...}
        for dic in studat[stu]:
            if "video" in dic["event_type"]:    # only considering video events
                try:
                    tmpsesh = dic["session"]
                    tmptime = datetime.datetime.strptime(dic["time"][:-6], '%Y-%m-%dT%H:%M:%S.%f' if '.' in dic["time"] else '%Y-%m-%dT%H:%M:%S')
                    if tmpsesh in sesh_times:
                        # then initial time is already there, update end time:
                        sesh_times[tmpsesh][1] = tmptime
                    else:
                        # then start a new session entry:
                        sesh_times[tmpsesh] = [tmptime, tmptime]
                except KeyError:
                    # filters problems out (NOTE: already done with 'video' update)
                    continue

        # now take difference of each session and add to total time of student:
        tottime = datetime.timedelta(0)
        for sesh in sesh_times:
            # TODO: make sure time is in proper format to subtract
            tottime += sesh_times[sesh][1] - sesh_times[sesh][0]

        # and add to the allstu dict:
        allstu[stu] = tottime.total_seconds()

    return allstu


def feat12(studat):
    """FEATURE: difference in average number of submissions per problem when
       compared to previous week
       input: time-sorted data, grouped by student
    """
    # NOTE: special case where week is part of feature definition
    # take "current" week to be latest date (so that it still works for
    # selecting new week by limiting input data)
    pass


def feat13(studat):
    """FEATURE: difference in ratio of total time spent to number of distinct
       correct problems compared to previous week
       input: time-sorted data, grouped by student
    """
    # NOTE: special case where week is part of feature definition
    # take "current" week to be latest date (so that it still works for
    # selecting new week by limiting input data)

    pass


def feat14(studat):
    """FEATURE: difference in ratio of number of problems attempted to number of
       distinct correct problems compared to previous week
       input: time-sorted data, grouped by student
    """
    # NOTE: special case where week is part of feature definition
    # take "current" week to be latest date (so that it still works for
    # selecting new week by limiting input data)

    pass


def feat15(studat):
    """FEATURE: difference in average time to solve problems compared to
       previous week
       input: time-sorted data, grouped by student
    """
    # NOTE: special case where week is part of feature definition
    # take "current" week to be latest date (so that it still works for
    # selecting new week by limiting input data)
    pass


def feat16(studat):
    """FEATURE: number of correct submissions
       input: time-sorted data, grouped by student
    """
    # NOTE: ignore; identical to feature 5 (?)
    pass


def feat17(studat):
    """FEATURE: percentage of the total submissions that were correct [x16 / x4]
       input: time-sorted data, grouped by student
    """
    # NOTE: ignore; identical to feature 8 (?)
    pass


def feat18(studat):
    """FEATURE: average time between a problem submission and problem due date
       over each submission that week
       input: time-sorted data, grouped by student
    """
    # TODO: find problem due date
    # (then refer to feature 9)

    pass


def feat19(studat):
    """FEATURE: standard deviation of duration of the events for the learner
       input: time-sorted data, grouped by student
    """
    # --------------
    # NOTE: considering durations of all session types
    # --------------
    allstu = {}
    for stu in studat:
        # for each student...
        sesh_times = {}
        # {'session1': [start, endtime], 'session2': [start, endtime], etc...}
        for dic in studat[stu]:
            try:
                tmpsesh = dic["session"]
                tmptime = datetime.datetime.strptime(dic["time"][:-6], '%Y-%m-%dT%H:%M:%S.%f' if '.' in dic["time"] else '%Y-%m-%dT%H:%M:%S')
                if tmpsesh in sesh_times:
                    # then initial time is already there, update end time:
                    sesh_times[tmpsesh][1] = tmptime
                else:
                    # then start a new session entry:
                    sesh_times[tmpsesh] = [tmptime, tmptime]
            except KeyError:
                continue

        # now take difference of each session and add to total time of student:
        durationlst = []
        for sesh in sesh_times:
            durationlst.append((sesh_times[sesh][1] - sesh_times[sesh][0]).total_seconds())

        # and add to the allstu dict:
        allstu[stu] = np.std(durationlst)

    return allstu

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


# ==================== PUTTING IT ALL TOGETHER =================================
def main():
    for course in COURSES:
        # open data from above global course name:
        openname = course[:].replace("-", "_")

        # make dict of course start dates:
        startdict = {'BerkeleyX_Stat_2.1x_1T2014': datetime.datetime(2014, 2, 23, 23, 0, 0, 0),
                     'DelftX_AE1110x_1T2014': datetime.datetime(2014, 2, 24, 0, 30, 0, 0),
                     'DelftX_AE1110x_2T2015': datetime.datetime(2015, 6, 2, 16, 0, 0, 0),
                     'DelftX_EX101x_1T2015': datetime.datetime(2015, 3, 31, 8, 0, 0, 0),
                     'DelftX_EX101x_3T2015': datetime.datetime(2015, 8, 31, 8, 0, 0, 0)}

        # OPENING ON SERVER:
        try:
            f = open("/deepedu/research/moocdrop/code/ORDERED_" + openname + ".log", "r")
        # account for inconsistent naming:
        except IOError:
            f = open("/deepedu/research/moocdrop/code/ORDERED_" + openname + "-events.log", "r")
        # TESTING ON LOCAL MACHINE:
        # f = open('testing.log', 'r')

        rawdat = f.readlines()
        f.close()

        # and repeat for each set of weeks [NOTE: 5 weeks is the limit!]:
        for week in range(1,6):
            # get data sorted by student:
            studat = stusort(rawdat, startdict[openname] + datetime.timedelta(weeks = week))
            # check original number of students:
            print(len(studat))

            # remove students that didn't do any event before week 1:
            slackerlst = []
            for stu in studat:
                # get first event:
                firstdic = studat[stu][0]

                # check the time:
                messytime = firstdic['time'][:-6]
                firsttime = datetime.datetime.strptime(messytime, '%Y-%m-%dT%H:%M:%S.%f' if '.' in messytime else '%Y-%m-%dT%H:%M:%S')

                # and compare to course start date:
                if firsttime > (startdict[openname] + datetime.timedelta(days = 7)):
                    # then record to remove! starting too late to consider for only 5 weeks
                    slackerlst.append(stu)

            for slacker in slackerlst:
                del studat[slacker]
            if '' in studat:
                del studat['']

            # Check number of remaining students:
            print(len(studat))

            # # number of items to print in each feature result:
            # testnum = 20
            #
            # # and shorten for testing:
            # studat = {stu:studat[stu] for stu in list(studat.keys())[:testnum]}

            feat_dic = {'1':feat1,'2':feat2,'3':feat3,'4':feat4,'5':feat5,'6':feat6,
                        '7':feat7,'8':feat8,'9':feat9,'10':feat10,'11':feat11,'12':feat12,
                        '13':feat13,'14':feat14,'15':feat15,'16':feat16,'17':feat17,
                        '18':feat18,'19':feat19}

            # extensively print results
            # for f in FEATURES:
            #     print("\nFeature " + str(f)+ ": " + str(feat_dic[str(f)](studat)))

            # ===================================================
            # put into csv for ensemble method code:
            final_studat = {}
            tracking = 0
            for f in FEATURES:
                if f == 9:
                    tmp_featresults = feat_dic[str(f)](studat, course)
                else:
                    tmp_featresults = feat_dic[str(f)](studat)

                # and add to the final results
                for stu in tmp_featresults:
                    if stu in final_studat:  # then append result to that student's list
                        final_studat[stu].append(tmp_featresults[stu])
                    else:  # then created new entry
                        # (-1 indicates no entries)
                        final_studat[stu] = [-1 for i in range(tracking)] + [tmp_featresults[stu]]

                # now append a -1 for any student left out in latest feature results:
                for stu in final_studat:
                    if stu not in tmp_featresults:
                        final_studat[stu].append(-1)

                tracking += 1
            # print(final_studat)

            # .................................. OUTPUT ................................
            # then output final_studat in csv
            f_res = open('FEATURES_' + course + '.csv', 'a')
            # HEADER (only at the top)
            if week == 1:
                f_res.write('user_id,week')
                for i in range(len(FEATURES)):
                    f_res.write(',feature' + str(i+1))
                f_res.write('\n')
            # FEATURES (and week)
            for stu in final_studat:
                f_res.write(stu.replace('username_',''))
                f_res.write(',' + str(week))
                for i in final_studat[stu]:
                    if i == -1 or math.isnan(i):     # put nothing if value wasn't found
                        f_res.write(',')
                    else:
                        f_res.write(',' + str(i))
                f_res.write('\n')
            f_res.close()


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Call to execute main():
if __name__ == "__main__": main()
