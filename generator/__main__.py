import sys
import click
from configparser import ConfigParser
from functools import wraps
from time import time
from tqdm import tqdm
from progress.bar import ChargingBar

from .patient_generator import generate_patient, generator_set_up

from .helpers_csv import append_to_csv

from concurrent.futures import ProcessPoolExecutor, as_completed

# read the configuration file
parser = ConfigParser()
parser.read('config.ini')

# population to produce
population_size = int(parser.get('generate', 'population_size'))

def timing(f):
    """
    A function that prints out execution time of the whole application
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time()
        result = f(*args, **kwargs)
        print(f"Generation and data saving executed in: {(time() - start):.3f} seconds.")
        return result
    return wrapper

@click.command()
@click.option('--prob', is_flag=True, help="Display probability details")
@click.option('--display', is_flag=True, help="Display patient details while populating")
@click.option('--population', '-p', default=population_size, \
                help='How many patients to produce')
@timing
def main(population, display, prob):
    """The main routine."""
    start_time = time()
    country, demographics, deprivation, ages, modules = generator_set_up()
    with ProcessPoolExecutor(max_workers=5) as pool:
        print(f"Starting generation of {population:,} patients.")
        # set up lists for generated data
        patients = []
        timelines = []
        futures = []
        for i in tqdm(range(population)):
            futures.append(pool.submit(generate_patient, country, demographics, deprivation, ages, modules, display, prob))

        print(f"Generation executed in {(time() - start_time):.3f} seconds.")

        bar = ChargingBar("Saving to CSV", max=population)
        for x in as_completed(futures):
            patients.append(x.result()[0])
            timelines.append(x.result()[1:])
            bar.next()
        bar.finish()

        # append them to relevant CSVs
        append_to_csv('output/patients.csv', patients)
        [append_to_csv('output/timelines.csv', timeline) for timeline in timelines]

        

if __name__ == "__main__":
    exit(main())