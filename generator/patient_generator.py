#!/usr/bin/python3

from pandas import read_csv
from time import time
from tqdm import tqdm
from configparser import ConfigParser

# import helper functions
from .helpers_id import generate_nhi_id, generate_random_id
from .helpers_patient import select_region, select_area, select_ethnicity, \
    select_gender, select_age, calculate_age, match_deprivation 
from .helpers_csv import create_csv, append_to_csv
from .helpers_timelines import  set_initial_prob, run_module
# import patient class
from .patient_class import Patient

start_time = time()

# read the configuration file
parser = ConfigParser()
parser.read('config.ini')

# get the country
country = parser.get('generate', 'country')

# get the demographic data and deprivation data
demographics_loc = parser.get(country, 'demographics')
deprivation_loc = parser.get(country, 'deprivation')

# iterate over modules for that location and create a dictionary
modules = {}
for module, data in parser.items(''.join([country, '_modules'])):
    modules[module] =  read_csv(data)

# import demographics and deprivation
demographics = read_csv(demographics_loc)
deprivation = read_csv(deprivation_loc)

# set a list of possible age ranges
ages = ['0_4',	'5_9',	'10_14', '15_19',	'20_24',	'25_29', '30_34',	'35_39', \
        '40_44',	'45_49',	'50_54',	'55_59',	'60_64',	'65_69',	'70_74', \
        '75_79',	'80_84',	'85_']

# set up output files for patients and timelines
header_patient = "id,region,area,ethnicity,gender,age_range,dob,deprivation_level"
create_csv('output/patients.csv', header_patient)
header_timeline = "id,age_range"
for module in modules:
    header_timeline += ',' + module
create_csv('output/timelines.csv', header_timeline)

def generate_patients(population, display, debug):
    """
    Patient and timeline generator
    Parameters:
        population: an integer value for the number of patients to generate
        display: a boolean value, whether to display patient information while generating
        debug: boolean, whether to show debugging information
    Returns:
        None
    """
    # generate the specified number of patients
    for _ in tqdm(range(1, int(population)+1)):

        ## Patient generation
        # generate information for a patient
        # if country id NZ, generate NHI number
        if country == 'NZ':
            id = generate_nhi_id()
        else:
            id = generate_random_id()
        region = select_region(demographics)
        area = select_area(demographics, region)
        ethnicity = select_ethnicity(demographics, region, area)
        gender = select_gender(demographics, region, area, ethnicity)
        dob, age_range = select_age(demographics, region, area, ethnicity)
        deprivation_level = match_deprivation(deprivation, area)
        age = calculate_age(dob)

        # generate a patient object
        patient = Patient(id, region, area, ethnicity, gender, age_range, dob, age, deprivation_level)

        # save to patients' file
        data = [patient.id, patient.region, patient.area, \
                patient.ethnicity, patient.gender, \
                patient.age_range, patient.dob, \
                patient.deprivation_level]
        append_to_csv('output/patients.csv', data)

        if debug:
            print(f"===================================================================================================")
            print(f"Current patient: {patient.id}, age: {patient.age}, ethnicity: {patient.ethnicity}, gender: {patient.gender}, deprivation: {patient.deprivation_level}")
            print(f"===================================================================================================")

        ## Set up initial probabilities for all modules
        # create a dictionary of modules
        # to store transition probabilities
        module_dict = {}
        for module, data in modules.items():
            states, t_probabilities, m_probabilities = set_initial_prob(module, data, patient.__dict__, debug)
            # add the states, transition probabilities and transition multiplications to the module dictionary
            module_dict[module] = (states, t_probabilities, m_probabilities, '')

        ## Timeline generation
        # get the index of the current age range from the list plus 1
        index = ages.index(patient.age_range) + 1
        # set up an emtpy dictionary for timeline records
        timelines_dict = {}
        # set up previous timeline as an empty dictionary, to be used for the first record
        previous_timeline = {}


        # iterate through ages until max age range
        for age in zip(range(index), ages):

            # create an empty dictionary to use as module results
            current_timeline = {}

            # iterate through each module and run it
            for module, data in modules.items():
                # run the module and extract result
                new_state, new_module_dict = run_module(module, data, age[1], patient.__dict__, current_timeline, previous_timeline, module_dict, debug)
                # result should be a selected status for that age range and module
                current_timeline[module] = new_state
                # update the module_dict
                module_dict = new_module_dict

            # amend previous timeline to a copy of the current timeline
            # it will be used by the next timeline iteration
            previous_timeline = current_timeline.copy()

            # after all modules run, add it to the timelines dictionary
            timelines_dict[age[1]] = current_timeline

            # save to timelines' file
            data = [patient.id, age[1]] + list(current_timeline.values())
            append_to_csv('output/timelines.csv', data)
        # add the timelines to the patient object
        patient.timelines = timelines_dict

        if display:
            print(f"Patient: {patient.id}, {patient.region}, {patient.area}, {patient.gender}, {patient.ethnicity}, {patient.age_range}, {patient.dob}")

    print(f"Executed in {(time() - start_time)/60} minutes.")
