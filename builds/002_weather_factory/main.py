import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description='Weather CLI App')
    parser.add_argument('-c', '--city', type=str, help='Specify the city to get weather information for', required=True)
    parser.add_argument('-u', '--units', type=str, choices=['C', 'F'], help='Choose units: Celsius (C) or Fahrenheit (F)', default='C')
    parser.add_argument('-v', '--verbose', action='store_true', help='Increase verbosity of output')
    return parser.parse_args()


def main():
    args = parse_arguments()
    city = args.city
    units = args.units
    verbose = args.verbose

    # TODO: Integrate with weather_api and format output using formatter

    if verbose:
        print(f'Getting weather information for {city} in {units} units...')
    else:
        print(f'Weather for {city}: ...')


if __name__ == '__main__':
    main()
