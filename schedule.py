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

EXIT_NUM = 100000
try:
    EXIT_NUM = int(os.environ['MAX'])
except:
    pass


parser = argparse.ArgumentParser(description='Script for determining the optimal student-teacher schedule. Will force into the provided number of timeslots and return the leftover teachers to be slotted.')
parser.add_argument('csv_filename', type=str, help='Required - Filename of CSV file of students and their teachers.')
parser.add_argument('timeslots', type=int, help='Required - Number of timeslots to force into. Will return remaining teachers')

args = parser.parse_args()
filename = args.csv_filename
num_timeslots = args.timeslots

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
        return 'Timeslot: \n    ' +  '\n    '.join([s + str(student_teacher_dict[s]) for s in self.students])

    def add_student(self,student):
        self.students.append(student)

    def determine_available_teachers(self):
        busy_teachers = set()
        for student in self.students:
            busy_teachers = busy_teachers.union(student_teacher_dict[student])
        return all_teachers - busy_teachers

    def get_students(self):
        return self.students

    def copy(self):
        debug(self.students)
        copy_of_self = Timeslot(self.students.copy())
        return copy_of_self


class Schedule:
    
    timeslots = []
    
    def __init__(self):
        pass
    
    def students_scheduled(self):
        scheduled_students = set()
        for ts in self.timeslots:
            scheduled_students.update(ts.get_students())
        return scheduled_students

    def students_left(self):
        return all_students - self.students_scheduled()

    def __str__(self):
        return f"Schedule ({len(self.timeslots)} timeslots):\n\n" + '\n'.join([str(t) for t in self.timeslots]) + f'\n\nwith leftover students:\n    ' + '\n    '.join([s + str(student_teacher_dict[s]) for s in self.students_left()])

    def determine_possible_timeslots_for(self,student):
        possible_timeslots = []
        for ts in self.timeslots:
            available_teachers = ts.determine_available_teachers()
            if student_teacher_dict[student].issubset(available_teachers):
                possible_timeslots.append(ts)
        return possible_timeslots

    def is_availability(self,students):
        for s in students:
            if len(self.determine_possible_timeslots_for(s)):
                return True
        return False

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

    def meets_min_reqs(self):
        # for s in self.students_left():
        #     for ts in self.timeslots:
        #         available_teachers = ts.determine_available_teachers()
        #         debug(f'Needed teachers: {student_teacher_dict[s]}')
        #         debug(f'Available: {available_teachers}')
        #         unavailable_teachers = student_teacher_dict[s] - available_teachers
        #         debug(f'Unavailable: {unavailable_teachers}')
        #         if len(unavailable_teachers) > 5 and s != "Tiffany" and s != "Song":
        #             debug(s)
        #             debug(unavailable_teachers)
        #             return False
        # print("WE FOUND ONE")
        return True


min_leftover_students=len(all_students)
count=0
best_poss_scheds=[]
checked_left_students = set()

def remove_non_min_length(possible_schedules):
    global best_poss_scheds
    debug(f'Cleaning {possible_schedules}')
    global min_leftover_students
    for sched in possible_schedules:
        if len(sched.students_left()) < min_leftover_students:
            min_leftover_students = len(sched.students_left())
    min_scheds = []
    for sched in possible_schedules:
        # if len(sched.students_left()) <= min_leftover_students:
        if len(sched.students_left()) <= min_leftover_students and frozenset(sched.students_left()) not in checked_left_students and sched.meets_min_reqs():
            checked_left_students.add(frozenset(sched.students_left()))
            min_scheds.append(sched)
    best_poss_scheds = best_poss_scheds + min_scheds
    return min_scheds

def calc_possible_schedules(schedule : Schedule, students : list):
    global min_leftover_students
    global count

    debug(f'Checking studnets left over: {students}')

    count += 1
    # if count % 10000 == 0:
        # print(f'Count number {count}, min unscheduled so far: {min_leftover_students}')
        # print(f'Considering sched {schedule}')
    if EXIT_NUM and count > EXIT_NUM:
        print('EXITED EARLY: Possible schedules (minimal number of timeslots):')
        print()
        for possible_schedule in best_poss_scheds:
            print(possible_schedule)
            print()
        sys.exit(0)
    
    if frozenset(students) in checked_left_students:
        debug('Skipping because this set of left students doesnt work')
        return []

    if len(students) == 0:
        print('Found perfect schedule:')
        print(schedule)
        sys.exit(0)

    if schedule.num_timeslots() > num_timeslots:
        return []

    debug(f'Schedule so far: {schedule}')
    debug(f'Students left to schedule: {students}')

    possible_schedules = []
    
    # if len(students) > min_leftover_students:
    #     debug('Too many students left to schedule, Skipping...')
    #     return []

    if schedule.num_timeslots() == num_timeslots and not schedule.is_availability(students):
        # print('Exiting early - Possible schedules (minimal number of timeslots):')
        # print(schedule)
        # sys.exit(0)
        return [schedule]

    for student in students:
        debug(f'Scheduling student {student}...')

        students_left = students.copy()
        students_left.remove(student)
        for possible_timeslot in schedule.determine_possible_timeslots_for(student):
            possible_schedule = schedule.copy()
            possible_schedule.add_to(student,possible_timeslot)
            new_possible_schedules = calc_possible_schedules(possible_schedule,students_left)
            debug(f'New possible schedules (found timeslot fit): {new_possible_schedules}')
            possible_schedules.extend(new_possible_schedules)
        possible_schedule = schedule.copy()
        new_timeslot = Timeslot([student])
        possible_schedule.add(new_timeslot)
        debug(f'Calc possible schedules for {possible_schedule}')
        new_possible_schedules = calc_possible_schedules(possible_schedule,students_left)
        debug(f'New possible schedules (new timeslot): {new_possible_schedules}')
        possible_schedules.extend(new_possible_schedules)

    return remove_non_min_length(possible_schedules)
            

output = calc_possible_schedules(Schedule(),list(student_teacher_dict.keys()))
print('Possible schedules (minimal number of timeslots):')
print()
for possible_schedule in output:
    print(possible_schedule)
    print()