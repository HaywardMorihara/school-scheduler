#!/usr/bin/env python3

import argparse
import csv
import os

DEBUG_MODE=False
try:
    DEBUG_MODE = os.environ['DEBUG']
except:
    pass

parser = argparse.ArgumentParser(description='Script for determining the optimal student-teacher schedule.')
parser.add_argument('csv_filename', type=str, help='Required filename of CSV file of students and their teachers.')

args = parser.parse_args()
filename = args.csv_filename

student_teacher_dict = {}
all_teachers = set()

with open(filename, newline='') as student_teacher_csv:
    csv_reader = csv.reader(student_teacher_csv)
    for row in csv_reader:
        student = row[0]
        teachers_for_student = set([x for x in row[1:] if x != ''])
        all_teachers = all_teachers.union(teachers_for_student)
        student_teacher_dict[student] = set(teachers_for_student)

def debug(message):
    if DEBUG_MODE:
        print(message)

debug(student_teacher_dict)

def determine_available_teachers(timeslot):
    busy_teachers = set()
    for student in timeslot:
        busy_teachers = busy_teachers.union(student_teacher_dict[student])
    return all_teachers - busy_teachers

def student_fits_in(student,timeslot):
    available_teachers = determine_available_teachers(timeslot)
    return student_teacher_dict[student].issubset(available_teachers)

# def clean_singular_list(schedule):
#     debug(f'Cleaning {schedule}')
#     if not schedule:
#         return schedule
#     for x in schedule:
#         if len(x) != 1:
#             debug('fd')
#             return schedule
#     wrapped_list = []
#     print(f'Wrapping {schedule}')
#     wrapped_list.append(schedule)
#     print(f'Wrapped list: {wrapped_list}')
#     return wrapped_list

def calc_possible_schedules(schedule, students):
    debug(f'Schedule so far: {schedule}')
    debug(f'Students left to schedule: {students}')

    if len(students) == 0:
        debug(f'COMPLETE: Schedule {schedule} is complete!')
        return schedule

    possible_schedules = []
    student = students.pop()
    debug(f'Scheduling student {student}...')
    for timeslot in schedule:
        if student_fits_in(student,timeslot):
            possible_schedule = schedule.copy()
            possible_schedule.remove(timeslot)
            updated_timeslot = timeslot.copy()
            updated_timeslot.append(student)
            possible_schedule.append(updated_timeslot)
            new_possible_schedules = calc_possible_schedules(possible_schedule,students.copy())
            debug(f'New possible schedules (found timeslot fit): {new_possible_schedules}')
            possible_schedules.append(new_possible_schedules)
    possible_schedule = schedule.copy()
    new_timeslot = []
    new_timeslot.append(student)
    possible_schedule.append(new_timeslot)
    debug(f'Calc possible schedules for {possible_schedule}')
    new_possible_schedules = calc_possible_schedules(possible_schedule,students.copy())
    debug(f'New possible schedules (new timeslot): {new_possible_schedules}')
    # possible_schedule = clean_singular_list(new_possible_schedules)
    debug(f'Before extension: {possible_schedules}')
    possible_schedules.extend(new_possible_schedules)
    debug(f'After extension: {possible_schedules}')
    return possible_schedules
            

original_output = calc_possible_schedules([],list(student_teacher_dict.keys()))
debug(f'Output: {original_output}')
debug(f'Length of ouput: {len(original_output)}')
output = []
for o in original_output:
    debug(f'Cleaning {o}...')
    if len(o) != 1:
        output.append(o)
# debug(f'Output: {output}')
print(f'Found {len(output)} possible schdules:')
for option in output:
    print(option)