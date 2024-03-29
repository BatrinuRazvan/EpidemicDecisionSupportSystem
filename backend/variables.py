# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 10:41:59 2020
Document formated using VSCode default document formatting.

@author: DhalEynn
"""

from math import floor
from random import randint
import json


# -----------------------JSON CONFIG-------------------------------
def load_variables_from_json(json_path):
    try:
        with open(json_path, 'r') as json_file:
            json_data = json.load(json_file)

            global nb_of_people, number_of_months, number_of_days, start_sick, sleepTime, average_time_of_encounters
            global hard_encounters, max_chances_going_outside, time_incubating, time_before_infectious
            global max_infectuosity, max_lethality, days_before_possible_healing, healing_chances
            global immunity_bounds, immunity_random_increase, immunity_ri_start, immunity_modifier

            nb_of_people = json_data.get('nb_of_people', nb_of_people)
            number_of_months = json_data.get('number_of_months', number_of_months)
            number_of_days = json_data.get('number_of_days', number_of_days)
            start_sick = json_data.get('start_sick', start_sick)
            sleepTime = json_data.get('sleepTime', sleepTime)
            average_time_of_encounters = json_data.get('average_time_of_encounters', average_time_of_encounters)
            hard_encounters = json_data.get('hard_encounters', hard_encounters)
            max_chances_going_outside = json_data.get('max_chances_going_outside', max_chances_going_outside)
            time_before_infectious = json_data.get('time_before_infectious', time_before_infectious)
            max_infectuosity = json_data.get('max_infectuosity', max_infectuosity)
            max_lethality = json_data.get('max_lethality', max_lethality)
            days_before_possible_healing = json_data.get('days_before_possible_healing', days_before_possible_healing)
            healing_chances = json_data.get('healing_chances', healing_chances)
            immunity_random_increase = json_data.get('immunity_random_increase', immunity_random_increase)
            immunity_ri_start = json_data.get('immunity_ri_start', immunity_ri_start)
            immunity_modifier = json_data.get('immunity_modifier', immunity_modifier)

    except Exception as e:
        print(f"Error loading variables from JSON: {e}")
# --------------------------- VARIABLES TO CHANGE ------------------------------------

print_console = True
keep_logs = True
# Log level can be "DEBUG" (more detailed), "INFO" (normal) or "WARNING" (only important informations are kept)
log_level = "WARNING"
# Do you use Jupyter Notebook for executing or not
jupyterGraph = False

# Create people from 1 to "nb_of_people"
nb_of_people = 1000
# Duration of the experiment
number_of_months = 3
number_of_days = 0
# number of people who are sick at start
start_sick = 100

# Sleeping time for people
sleepTime = 8

# Average time for an encounter between 2 people, in hours
average_time_of_encounters = 3
# Are encounters hard ?
# False : easy encounters, people are only trying to encounter others available people
# True  : hard encounters, people will try to encounter everybody when outside, even people not available
hard_encounters = False
# Percentage of chances of someone available want to go outside
# Used as : if between 0 and max_chances_going_outside  -> go outside
#           if between 61 and max_chances_going_outside -> keep inside for an hour
max_chances_going_outside = 60

# Incubating time of the disease (in days).
# Determinate when you will start being in danger of passing away.
# Possible time is between these 2 values
time_incubating = [0, 8]
# Time before being infectious to others (in days)
time_before_infectious = 1
# Percent of max_infectuosity of the disease.
# Infectuosity can vary between max_infectuosity and "max_infectuosity-20"
max_infectuosity = 160 # Default 80
# Percent of max_lethality of the disease.
max_lethality = 10 # Default 2
# Days before a person can be healed when his disease has incubated
days_before_possible_healing = 0
# Probability to be healed each day from the disease after it has incubated
# Healing chances can vary between healing_chances and "healing_chances-10"
healing_chances = 45 # Default 90
# The immunity of a person to the disease is first taken at random between these bounds.
immunity_bounds = [0, 100]
# If True, randomly increase the immunity of a healed person with a value between immunity_ri_start and immunity_ri_start + immunity_modifier.
immunity_random_increase = True
immunity_ri_start = 20
# If a person heal from the disease and immunity_random_increase is False, his immunity is increased flatly by this amount.
# Else, look at immunity_random_increase description
immunity_modifier = 50

# ----------------------------LOAD JSON-------------------------------------
json_file_path = 'D:\\Licenta\\EDSS\\EpidemicDecisionalSupportSystem\\parameters.json'
load_variables_from_json(json_file_path)
# --------------------------- DO NOT CHANGE ------------------------------------


def getStartSick():
    global start_sick, nb_of_people
    if (start_sick < 1):
        start_sick = 1
    if (start_sick > nb_of_people):
        start_sick = floor(nb_of_people * 0.01)
    return int(start_sick)


def getAverageEncountersTime():
    global average_time_of_encounters
    if (average_time_of_encounters < 1):
        average_time_of_encounters = 1
    return int(average_time_of_encounters)


def getMaxChancesGoingOutside():
    global max_chances_going_outside
    if (max_chances_going_outside > 100):
        max_chances_going_outside = 100
    if (max_chances_going_outside < 0):
        max_chances_going_outside = 0
    return int(max_chances_going_outside)


def getMaxInfectuosity():
    global max_infectuosity
    if (max_infectuosity > 100):
        max_infectuosity = 100
    if (max_infectuosity < 0):
        max_infectuosity = 0
    if (max_infectuosity < 20):
        return randint(0, max_infectuosity)
    return randint(max_infectuosity - 20, max_infectuosity)


def getMaxLethality():
    global max_lethality
    if (max_lethality > 100):
        max_lethality = 100
    if (max_lethality < 0):
        max_lethality = 0
    return int(max_lethality)


def getHoursBeforeHeal():
    global days_before_possible_healing
    if (days_before_possible_healing < 0):
        days_before_possible_healing = 0
    return int(days_before_possible_healing * 24)


def getHoursBeforeInfectious():
    global time_before_infectious
    if (time_before_infectious < 0):
        time_before_infectious = 0
    return int(time_before_infectious * 24)


def getTimeIncubating():
    global time_incubating
    temp_incubating = [min(time_incubating[0], time_incubating[1]), max(
        time_incubating[0], time_incubating[1])]
    if (temp_incubating[0] < 0):
        temp_incubating[0] = 0
    if (temp_incubating[1] < 0):
        temp_incubating[1] = 0
    return randint(floor(temp_incubating[0] * 24), floor(temp_incubating[1] * 24))


def getHealingChances():
    global healing_chances
    if (healing_chances > 100):
        healing_chances = 100
    if (healing_chances < 0):
        healing_chances = 0
    if (healing_chances < 10):
        return randint(0, healing_chances)
    return randint(healing_chances - 10, healing_chances)


def getImmunity():
    global immunity_bounds
    immunity = randint(immunity_bounds[0], immunity_bounds[1])
    if (immunity > 100):
        immunity = 100
    if (immunity < 0):
        immunity = 0
    return immunity


def getIncreasedImmunity(old_immunity):
    """Increase the value of the input like it is documented for "immunity_modifier" in variables.py"""
    if (old_immunity >= 100):
        return 100
    global immunity_ri_start, immunity_modifier, immunity_random_increase
    if (immunity_random_increase):
        temp = old_immunity + \
            randint(immunity_ri_start, immunity_ri_start + immunity_modifier)
    else:
        temp = old_immunity + immunity_modifier
    if (temp > 100):
        temp = 100
    if (temp < 0):
        temp = 0
    return temp


# Number of days of the experience
lenght_experiment = abs(number_of_months * 30 +
                        floor(number_of_months / 2) +
                        number_of_days)


if (time_before_infectious < 0):
    time_before_infectious = 0

if (average_time_of_encounters < 0):
    average_time_of_encounters = 0