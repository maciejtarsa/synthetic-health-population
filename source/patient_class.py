#!/usr/bin/python3

# a file containing the specificiation of class Patient

class Patient:

    # variables?


    # constructor
    def __init__(self, id, region, area, ethnicity, gender, age_range, dob, deprivation_level):
        self.id = id
        self.region = region
        self.area = area
        self.ethnicity = ethnicity
        self.gender = gender
        self.age_range = age_range
        self.dob = dob
        self.deprivation_level = deprivation_level
        self.timelines = {}
        
