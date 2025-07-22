import argparse
import requests
import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Use existing environment variables
WEB_HOST = os.environ.get('NEXT_PUBLIC_WEB_HOST', 'localhost')
CONTROL_SERVER_PORT = os.environ.get('CONTROL_SERVER_PORT', '65508')
DEFAULT_CONTROL_SERVER_URL = f'http://{WEB_HOST}:{CONTROL_SERVER_PORT}'

def set_valve(valve_index, state, base_url):
    url = f'{base_url}/valve'
    resp = requests.post(url, json={'valveIndex': valve_index, 'state': state})
    print(resp.text)

def set_compressor(state, base_url):
    url = f'{base_url}/compressor'
    resp = requests.post(url, json={'value': state})
    print(resp.text)

def set_pressure_threshold(threshold, base_url):
    url = f'{base_url}/pressure-threshold'
    resp = requests.post(url, json={'threshold': threshold})
    print(resp.text)

def set_lower_pressure_threshold(threshold, base_url):
    url = f'{base_url}/lower-pressure-threshold'
    resp = requests.post(url, json={'threshold': threshold})
    print(resp.text)

def get_status(base_url):
    url = f'{base_url}/status'
    resp = requests.get(url)
    print(resp.text)

def main():
    parser = argparse.ArgumentParser(description='Control client for valve, compressor, and pressure threshold.')
    parser.add_argument('--host', type=str, default=DEFAULT_CONTROL_SERVER_URL,
                      help=f'Control server base URL (default: {DEFAULT_CONTROL_SERVER_URL})')
    subparsers = parser.add_subparsers(dest='command')

    # Valve
    parser_valve = subparsers.add_parser('valve', help='Toggle a valve')
    parser_valve.add_argument('index', type=int, help='Valve index (0, 1, 2)')
    parser_valve.add_argument('state', type=str, choices=['on', 'off'], help='Valve state')

    # Compressor
    parser_compressor = subparsers.add_parser('compressor', help='Toggle compressor')
    parser_compressor.add_argument('state', type=str, choices=['on', 'off'], help='Compressor state')

    # Pressure threshold
    parser_threshold = subparsers.add_parser('threshold', help='Set pressure threshold')
    parser_threshold.add_argument('value', type=float, help='Pressure threshold value')

    # Lower Pressure threshold
    parser_lower_threshold = subparsers.add_parser('lower-threshold', help='Set lower pressure threshold to turn off all valves')
    parser_lower_threshold.add_argument('value', type=float, help='Lower pressure threshold value')

    # Status
    parser_status = subparsers.add_parser('status', help='Get current status')

    args = parser.parse_args()
    base_url = args.host.rstrip('/')

    if args.command == 'valve':
        set_valve(args.index, args.state == 'on', base_url)
    elif args.command == 'compressor':
        set_compressor(args.state == 'on', base_url)
    elif args.command == 'threshold':
        set_pressure_threshold(args.value, base_url)
    elif args.command == 'lower-threshold':
        set_lower_pressure_threshold(args.value, base_url)
    elif args.command == 'status':
        get_status(base_url)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main() 