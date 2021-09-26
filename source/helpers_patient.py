#!/usr/bin/python3
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
from random import randrange
from datetime import timedelta

def select_region(demographics):
  """
  Selects a region based on provided demographics
  Parameters:
    demographics: a dataframe of demographics
  Returns:
    region: a string containing selected region
  """
  # get a list of regions with their population totals
  regions = demographics.groupby('Region').sum()
  # calculate frequencies
  regions['freq'] = regions['Population']/regions['Population'].sum()
  # select region
  region = random.choices(regions.index, regions['freq'], k=1)[0]
  return region

def select_area(demographics, region):
  """
  Selects an area based on provided demographics and region
  Parameters:
    demographics: a dataframe of demographics
    region: a string containing selected region
  Returns:
    area: a string containing selected area
  """
  # get a list of areas within the regions with their populations
  areas = demographics.loc[demographics['Region'] == region]
  # sum different ethnicities by area
  areas = areas.groupby('Area').sum()
  # calculate freqiencies
  areas['freq'] = areas['Population']/areas['Population'].sum()
  # select an area
  area = random.choices(areas.index, areas['freq'], k=1)[0]
  return area

def select_ethnicity(demographics, region, area):
  """
  Selects an ethnicity based on provided demographics, region and area
  Parameters:
    demographics: a dataframe of demographics
    region: a string containing selected region
    area: a string containing selected area
  Returns:
    ethnicity: a string containing selected ethnicity
  """
  # create a dataframe with only specified region and area
  ethnicities = demographics.loc[demographics['Region'] == region]
  ethnicities = ethnicities.loc[ethnicities['Area'] == area]
  # calculate freqiencies
  ethnicities['freq'] = ethnicities['Population']/ethnicities['Population'].sum()
  # select ethnicity
  ethnicity = random.choices(list(ethnicities['Ethnicity']), list(ethnicities['freq']), k=1)[0]
  return ethnicity

## select gender
def select_gender(demographics, region, area, ethnicity):
  """
  Selects gender based on provided demographics, region, area and ethnicity
  Parameters:
    demographics: a dataframe of demographics
    region: a string containing selected region
    area: a string containing selected area
    ethnicity: a string containing selected ethnicity
  Returns:
    gender: a string containing selected gender
  """
  # create a dataframe with only specified region, area and ethnicity
  gender = demographics.loc[demographics['Region'] == region]
  gender = gender.loc[gender['Area'] == area]
  gender = gender.loc[gender['Ethnicity']== ethnicity]
  # transpose the dataframe
  gender_t = gender[['Male','Female']].T
  # select gender
  gender = random.choices(list(gender_t.index), gender_t.values, k=1)[0]
  return gender

def select_age(demographics, region, area, ethnicity):
  """
  Selects age based on provided demographics, region, area and ethnicity
  Parameters:
    demographics: a dataframe of demographics
    region: a string containing selected region
    area: a string containing selected area
    ethnicity: a string containing selected ethnicity
    gender: a string containing selected gender
  Returns:
    dob: a randomly generated date of birth
    age_range: a string containing selected age range
  """
  # create a dataframe with only specified region, area and ethnicity
  age = demographics.loc[demographics['Region'] == region]
  age = age.loc[age['Area'] == area]
  age = age.loc[age['Ethnicity']== ethnicity]
  # only keep the columns with age
  age = age.iloc[:,6:24]
  # transpose
  age_t = age.T
  # select a random age range
  age_range = random.choices(list(age_t.index), age_t.values, k=1)[0]
  # extract the low and high values
  age_low, age_high = age_range.split('_')
  # check if that the age range is 85 and above
  if age_high == '':
    # if it is, change the high to 110 - a maximum age a person can be
    age_high = '110'
  # get age range to select from
  date_range = get_date_range(age_low, age_high)
  # generate random dob
  dob = generate_DOB(date_range[0], date_range[1])
  return dob, age_range

# helper function
# calculate the start date and end date from the date range
def get_date_range(age_low, age_high):
  """
  Calculates the start date and end date based on given age range
  Parameters:
    age_low: a string containing lowest age range
    age_high: a string containing highest age range
  Returns:
    a tuple containing start date and end date
  """
  end_date = datetime.date(datetime.now() - relativedelta(years=int(age_low)))
  start_date = datetime.date(datetime.now() - relativedelta(years=int(age_high)))
  return (start_date, end_date)

# helper function
# generate a random DOB based on start and end dates
def generate_DOB(start_date, end_date):
  """
  Generated a random date of birth based on start date and end date
  Parameters:
    start_date: earliest date
    end_date: lastest date
  Returns:
    dob: randomly generated dob
  """
  delta = end_date - start_date
  int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
  random_second = randrange(int_delta)
  return start_date + timedelta(seconds=random_second)

# helper function
# match deprivation score to the generated area
def match_deprivation(deprivation, area):
  """
  Match the area selected to the deprivation score
  Parameters:
    deprivation: a dataframe of deprivation scored
    area: selected area
  Returns:
    deprivation_score: a score matched to the area
  """
  # extract the score based on area name
  score = deprivation.loc[deprivation['area'] == area]['NZDep2018']
  # if location found
  if len(score) != 0:
    score = score.values[0]
  # otherwise, use the average of all areas
  else:
    score = deprivation['NZDep2018'].mean()
    # rounded to nearest integer
    score = round(score)
  return score

