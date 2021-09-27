# synthetic-health-population
An algorithm to use publicly available health statistics in order to generate a synthetic health population of an area.

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
generate_patients
```
Specify number of patients
```
generate_patients -p 2
```
or
```
generate_patients --population 2
```
print information about each patient
```
generate_patients --print
```
## Output
The applications saves the results to two csv files named `patients.csv` and `timelines.csv` located in the `outputs` folder.
