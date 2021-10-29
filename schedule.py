#!/usr/bin/env python3

import argparse
import csv
import os
import sys

DEBUG_MODE=False
try:
    DEBUG_MODE = os.environ['DEBUG']
except:
    pass

FIND_ONE=True
try:
    FIND_ONE = os.environ['FIND_ONE']
except:
    pass


parser = argparse.ArgumentParser(description='Script for determining the optimal student-teacher schedule.')
parser.add_argument('csv_filename', type=str, help='Required filename of CSV file of students and their teachers.')
parser.add_argument('max_timeslots', type=int, help='Required max acceptable timeslots - the lower this number, the faster this will run.')

args = parser.parse_args()
filename = args.csv_filename
current_max = args.max_timeslots

student_teacher_dict = {}
all_teachers = set()

with open(filename, newline='') as student_teacher_csv:
    csv_reader = csv.reader(student_teacher_csv)
    for row in csv_reader:
        student = row[0]
        teachers_for_student = set([x for x in row[1:] if x != ''])
        all_teachers = all_teachers.union(teachers_for_student)
        student_teacher_dict[student] = set(teachers_for_student)

all_students = set(student_teacher_dict.keys())

def debug(message):
    if DEBUG_MODE:
        print(message)

debug(student_teacher_dict)

class Timeslot:
    
    students = []
    
    def __init__(self, students):
      self.students = students
    
    def __str__(self):
        return f'Timeslot: {self.students}'

    def add_student(self,student):
        self.students.append(student)

    def determine_available_teachers(self):
        busy_teachers = set()
        for student in self.students:
            busy_teachers = busy_teachers.union(student_teacher_dict[student])
        return all_teachers - busy_teachers

    def copy(self):
        debug(self.students)
        copy_of_self = Timeslot(self.students.copy())
        return copy_of_self


class Schedule:
    
    timeslots = []
    
    def __init__(self):
        pass
    
    def __str__(self):
        return "Schedule: \n" + '\n'.join([str(t) for t in self.timeslots])

    def determine_possible_timeslots_for(self,student):
        possible_timeslots = []
        for ts in self.timeslots:
            available_teachers = ts.determine_available_teachers()
            if student_teacher_dict[student].issubset(available_teachers):
                possible_timeslots.append(ts)
        return possible_timeslots

    def add_to(self,student,timeslot):
        self.timeslots.remove(timeslot)
        new_timeslot = timeslot.copy()
        new_timeslot.add_student(student)
        self.timeslots.append(new_timeslot)

    def add(self,timeslot):
        self.timeslots.append(timeslot)

    def set(self, timeslots):
        self.timeslots = timeslots

    def copy(self):
        copy_of_self = Schedule()
        copy_of_self.set(self.timeslots.copy())
        return copy_of_self
    
    def num_timeslots(self):
        return len(self.timeslots)


def remove_non_min_length(possible_schedules):
    global current_max
    current_min = len(all_students)
    for sched in possible_schedules:
        if sched.num_timeslots() < current_min:
            current_min = sched.num_timeslots()
    if current_min < current_max:
        current_max = current_min
        print(f'New current max is {current_max}')
    min_scheds = []
    for sched in possible_schedules:
        if sched.num_timeslots() <= current_min:
            min_scheds.append(sched)
    return min_scheds


min_students=current_max

def calc_possible_schedules(schedule : Schedule, students : list):
    global min_students
    if len(students) < min_students:
        min_students = len(students)
        print(f'Closest we\'ve come: {min_students}')
    
    if len(students) == 0:
        if FIND_ONE == True:
            print(f'Found schedule with {schedule.num_timeslots()} timeslots')
            print(schedule)
            sys.exit(0)
        else:
            return [schedule]
    
    if schedule.num_timeslots() > current_max:
        debug("skip - won't be better")
        return []

    debug(f'Schedule so far: {schedule}')
    debug(f'Students left to schedule: {students}')

    possible_schedules = []
    student = students.pop()
    debug(f'Scheduling student {student}...')
    for possible_timeslot in schedule.determine_possible_timeslots_for(student):
        possible_schedule = schedule.copy()
        possible_schedule.add_to(student,possible_timeslot)
        new_possible_schedules = calc_possible_schedules(possible_schedule,students.copy())
        debug(f'New possible schedules (found timeslot fit): {new_possible_schedules}')
        possible_schedules.extend(new_possible_schedules)
    if schedule.num_timeslots() < current_max:
        possible_schedule = schedule.copy()
        new_timeslot = Timeslot([student])
        possible_schedule.add(new_timeslot)
        debug(f'Calc possible schedules for {possible_schedule}')
        new_possible_schedules = calc_possible_schedules(possible_schedule,students.copy())
        debug(f'New possible schedules (new timeslot): {new_possible_schedules}')
        possible_schedules.extend(new_possible_schedules)
    return remove_non_min_length(possible_schedules)
            

# ts1 = Timeslot(["A"])
# ts2 = Timeslot(["B"])
# s = Schedule()
# s2 = Schedule()
# possible_sc = [s,s2]
# print(possible_sc)

output = calc_possible_schedules(Schedule(),list(student_teacher_dict.keys()))
print('Possible schedules (minimal number of timeslots):')
print()
for possible_schedule in output:
    print(possible_schedule)
    print()