#!/usr/bin/python3

import pandas as pd
import csv
from configparser import ConfigParser

# import helper functions
from helpers_id import generateNHI, generateRandID
from helpers_patient import select_region, select_area, select_ethnicity, \
    select_gender, select_age, match_deprivation 
from helpers_csv import create_csv, append_to_csv
# import patient class
from patient_class import Patient

# read the configuration file
parser = ConfigParser()
parser.read('config.ini')

# get the country
country = parser.get('generate', 'country')

# population to produce
population_size = int(parser.get('generate', 'population_size'))

# get the demographic data and deprivation data
demographics_loc = parser.get(country, 'demographics')
deprivation_loc = parser.get(country, 'deprivation')

# iterate over modules for that location and create a dictionary
modules = {}
for module, data in parser.items(country+'_modules'):
    modules[module] =  pd.read_csv(data)

# import demographics and deprivation
demographics = pd.read_csv(demographics_loc)
deprivation = pd.read_csv(deprivation_loc)

# set a list of possible age ranges
ages = ['0_4',	'5_9',	'10_14', '15_19',	'20_24',	'25_29', '30_34',	'35_39', \
        '40_44',	'45_49',	'50_54',	'55_59',	'60_64',	'65_69',	'70_74', \
        '75_79',	'80_84',	'85_']

# set up an output files for patients and timeline
header_patient = "id,region,area,ethnicity,gender,age_range,dob,deprivation_level"
create_csv('output/patients.csv', header_patient)
header_timeline = "id,age_range"
for module in modules:
    header_timeline += ',' + module
create_csv('output/timelines.csv', header_timeline)

# generate the specified number of patients

for _ in range(1, population_size+1):

    ## Patient generation
    # generate information for a patient
    id = generateNHI()
    region = select_region(demographics)
    area = select_area(demographics, region)
    ethnicity = select_ethnicity(demographics, region, area)
    gender = select_gender(demographics, region, area, ethnicity)
    dob, age_range = select_age(demographics, region, area, ethnicity)
    deprivation_level = match_deprivation(deprivation, area)

    # generate a patient object
    patient = Patient(id, region, area, ethnicity, gender, age_range, dob, deprivation_level)

    # save to patients' file
    data = [patient.id, patient.region, patient.area, \
            patient.ethnicity, patient.gender, \
            patient.age_range, patient.dob, \
            patient.deprivation_level]
    append_to_csv('output/patients.csv', data)

    ## Timeline generation
    # get the index of the age range from the list plus 1
    index = ages.index(patient.age_range) + 1

    timelines_dict = {}

    # iterate through ages until index + 1 is met
    for age in zip(range(index), ages):
        # create a record for the dictionary
        timelines_dict[age[1]] = {}

        # save to patients' file
        #data = [patient.id, timelines_dict[age[1]]]
        #append_to_csv('output/timelines.csv', data)
    # add the timelines to the patient object
    patient.timelines = timelines_dict

    

    print(f"patient's timeline is: {patient.timelines}")

