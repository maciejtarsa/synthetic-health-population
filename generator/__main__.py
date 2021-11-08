import sys
import click
from configparser import ConfigParser
from functools import wraps
from time import time
from tqdm import tqdm

from .patient_generator import generate_patient, generator_set_up

from concurrent.futures import ProcessPoolExecutor

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
@click.option('--debug', is_flag=True, help="Display debugging details")
@click.option('--display', is_flag=True, help="Display patient details while populating")
@click.option('--population', '-p', default=population_size, \
                help='How many patients to produce')
@timing
def main(population, display, debug):
    """The main routine."""
    start_time = time()
    country, demographics, deprivation, ages, modules = generator_set_up()
    with ProcessPoolExecutor(max_workers=5) as pool:
        print(f"Starting generation of {population:,} patients.")
        for _ in tqdm(range(population)):
            pool.submit(generate_patient, country, demographics, deprivation, ages, modules, display, debug)
        print(f"Generation executed in {(time() - start_time):.3f} seconds.")

if __name__ == "__main__":
    exit(main())