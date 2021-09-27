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
@click.option('--print', is_flag=True, help="Print details while populating")
@click.option('--population', '-p', default=population_size, \
                help='How many patients to produce')
def main(population, print=False):
    """The main routine."""
    generate_patients(population, print)



if __name__ == "__main__":
    sys.exit(main())
