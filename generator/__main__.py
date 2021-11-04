import sys
import click
from configparser import ConfigParser
from time import time
from tqdm import tqdm
from .patient_generator import generate_patient

from concurrent.futures import ProcessPoolExecutor

# read the configuration file
parser = ConfigParser()
parser.read('config.ini')

# population to produce
population_size = int(parser.get('generate', 'population_size'))

@click.command()
@click.option('--debug', is_flag=True, help="Display debugging details")
@click.option('--display', is_flag=True, help="Display patient details while populating")
@click.option('--population', '-p', default=population_size, \
                help='How many patients to produce')
def main(population, display=False, debug=False):
    """The main routine."""
    start_time = time()
    with ProcessPoolExecutor(max_workers=5) as pool:
        print(f"Starting generation of {population:,} patients.")
        for _ in tqdm(range(population)):
            pool.submit(generate_patient,display, debug)
        
        print(f"Executed in {(time() - start_time)} seconds.")
        print(f"Please wait, the data is still being saved to CSV.")
        



if __name__ == "__main__":
    exit(main())