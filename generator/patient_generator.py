#!/usr/bin/python3

from pandas import read_csv

from configparser import ConfigParser

# import helper functions
from .helpers_id import generate_nhi_id, generate_random_id
from .helpers_patient import select_region, select_area, select_ethnicity, \
    select_gender, select_age, calculate_age, match_deprivation 
from .helpers_csv import create_csv, append_to_csv
from .helpers_timelines import  set_initial_prob, run_module
# import patient class
from .patient_class import Patient


def generator_set_up():
    """
    A function that sets up empty CSV files and loads in available modules
    Parameters:
        None
    Returns:
        country: specified country to generate patients for
        demographics: a DataFrame containing demographic information for that location
        deprivation: a DataFrame containing deprivation scores for selected location
        ages: a list of age ranges
        modules: a dictionary containing module information
    """
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
    print(f"===================================================================================================")
    print(f"Loading available modules:")
    for module, data in parser.items(''.join([country, '_modules'])):
        modules[module] =  read_csv(data)
        print(f"{module}")
    print(f"===================================================================================================")
    print()

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

    return country, demographics, deprivation, ages, modules
    

def generate_patient(country, demographics, deprivation, ages, modules, display=False, debug=False):
    """
    Patient and timeline generator
    Parameters:
        demographics: a DataFrame containing demographic information
        deprivation: a DataFrame contaning deprivation scores
        ages: a list of age ranges
        modules: a dictionary of module and probabilities
        display: a boolean value, whether to display patient information while generating
        debug: boolean, whether to show debugging information
    Returns:
        None
    """

    ## Patient generation
    # generate information for a patient
    # if country is NZ, generate NHI number
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
        print()
        print(f"===========================================================================================================================================")
        print(f"Current patient: {patient.id}, region: {patient.region}, area: {patient.area}, age: {patient.age}, ethnicity: {patient.ethnicity}, gender: {patient.gender}, deprivation: {patient.deprivation_level}")
        print(f"===========================================================================================================================================")

    ## Set up prior initial probabilities for all modules
    # create a dictionary of modules
    # to store prior state transition probabilities
    module_dict = {}
    for module, data in modules.items():
        states, prior_trans_prob = set_initial_prob(module, data, patient.__dict__, debug)
        # add the states, prior state transition probabilities and prior state multiplications to the module dictionary
        module_dict[module] = (states, prior_trans_prob,'')

    ## Timeline generation
    # get the index of the current age range from the list plus 1
    index = ages.index(patient.age_range) + 1
    # set up an emtpy dictionary for timeline records
    timelines_dict = {}
    # set up previous timeline as an empty dictionary, to be used for the first record
    previous_timeline = {}


    # iterate through ages until max age range
    for age in zip(range(index), ages):

        if debug:
            print()
            print(f"=====================")
            print(f"Age range: {age[1]}")

        # create an empty dictionary to use as module results
        current_timeline = {'age_range': age[1]}

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
        data = [patient.id] + list(current_timeline.values())
        append_to_csv('output/timelines.csv', data)
    # add the timelines to the patient object
    patient.timelines = timelines_dict

    if debug:
        print(f"===================================================================================================")
        print(f"Next patient")

    if display:
        print(f"Patient: {patient.id}, {patient.region}, {patient.area}, {patient.ethnicity}, {patient.gender}, {patient.age_range}, {patient.dob}, {patient.deprivation_level}")
