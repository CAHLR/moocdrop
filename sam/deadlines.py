# script to extract problem deadlines from messy MOOC data structure
import os
from bs4 import BeautifulSoup

# change to generate list for other classes
FOLDER = "DelftX-EX101x-3T2015"

# where to find vertical, sequential, and problem folders:
address = "/deepedu/research/moocdrop/data/" + FOLDER + "/"


def main():
    # start with sequential files and work down to problems
    # ==============================================================================
    # EXTRACTING INFO FROM SEQUENTIAL
    # ==============================================================================
    verts = {}  # dict of all verticals for that course
                # (value is due date from corresponding sequential)
    for filename in os.listdir(address + "sequential/"):
        f = open(address + "sequential/" + filename, "r")
        info = BeautifulSoup(f, "lxml")    # parsing of xml
        f.close()

        try:
            deadline = info.sequential["due"][:-1]  # removing "Z" at end of the date
            for i in info.findAll("vertical"):
                verts[i["url_name"]] = deadline
        except KeyError:
            # if sequential isn't a graded assignment with deadline... just ignore
            continue

    # ==============================================================================
    # EXTRACTING INFO FROM VERTICALS
    # ==============================================================================
    probs = {}  # dict of all graded problems for that course
                # (value is due date from corresponding sequential/vertical)
    for vert in verts:
        f = open(address + "vertical/" + vert + ".xml", "r")
        info = BeautifulSoup(f, "lxml")    # parsing of xml
        f.close()

        try:
            for i in info.findAll("problem"):
                probs[i["url_name"]] = verts[vert]  # setting problem to due date

        except KeyError:
            # if no problems assigned, just move on (not expected though)
            continue

    # now write all info to a log file in code directory for easy access later:
    f = open("/deepedu/research/moocdrop/code/DEADLINES_" + FOLDER + ".csv", "a")
    for p in probs:
        f.write(p + "," + probs[p] + "\n")
    f.close()

# Call to execute main():
if __name__ == "__main__": main()
