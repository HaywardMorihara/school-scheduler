#!/usr/bin/env python3

import argparse
import csv
from random import randint
from random import seed

parser = argparse.ArgumentParser(description='Script for generating random student/teacher data.')
parser.add_argument('num_students', type=int, help='Required number of total students.')
parser.add_argument('num_teachers', type=int, help='Required number of total teachers.')

args = parser.parse_args()
num_students = args.num_students
num_teachers = args.num_teachers

with open('gen_sample.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for i in range(1,num_students+1):
        writer.writerow([f'Student {i}', f'Teacher {randint(1,num_teachers)}', f'Teacher {randint(1,num_teachers)}', f'Teacher {randint(1,num_teachers)}', f'Teacher {randint(1,num_teachers)}'] )