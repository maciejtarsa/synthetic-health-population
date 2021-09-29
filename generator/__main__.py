import sys
import click
from configparser import ConfigParser
from .patient_generator import generate_patients

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
    generate_patients(population, display, debug)



if __name__ == "__main__":
    exit(main())
