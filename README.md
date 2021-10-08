# synthetic-health-population
An algorithm to use publicly available health statistics in order to generate a synthetic health population of an area.
## Settings
File `config.ini` contains setting for the application. Currently, a country to be used can be specified as well as population size to be produced
```
[generate]
# default country
country = NZ
# default size of population to produce
population_size = 5
```

## Input
Input for the application consists of a number of files referring to the country/area.<br><br>
In order to add a new area, two new sections need to be added to file `config.ini`, for example:<br>
New Zealand requires section [NZ] with locations for demographics and deprivation input files as well as [NZ_modules] section with location of lifestyle and disease modules input files
```
[NZ]
# input filed for NZ
demographics = input/nz/demographic/nz_demographics.csv
deprivation = input/nz/demographic/nz_deprivation.csv

[NZ_modules]
# lifestyle and disease moduled for NZ
smoking = input/nz/lifestyle/smoking.csv
physical_activity = input/nz/lifestyle/physical_activity.csv
body_size = input/nz/lifestyle/body_size.csv
diabetes_1 = input/nz/lifestyle/diabetes_1.csv
```
## Output
The applications saves the results to two csv files named `patients.csv` and `timelines.csv` located in the `outputs` folder.

## Installation
```
git clone https://github.com/maciejtarsa/synthetic-health-population
cd synthetic-health-population
python3 -m venv env
source env/bin/activate
python3 -m pip install --editable .
```
## Running
Move to the folder and run
```
cd synthetic-health-population
source env/bin/activate
generate_patients
```
### Possible options for running
#### Specify number of patients
```
generate_patients -p 2
```
or
```
generate_patients --population 2
```
#### print detailed information about probabilities and transitions for each state
```
generate_patients --debug
```
#### print information about each patient
```
generate_patients --print
```
