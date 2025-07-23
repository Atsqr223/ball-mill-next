import argparse
import requests
import sys

CONTROL_SERVER_URL = 'http://localhost:65507'

def set_valve(valve_index, state):
    url = f'{CONTROL_SERVER_URL}/valve'
    resp = requests.post(url, json={'valveIndex': valve_index, 'state': state})
    print(resp.text)

def set_compressor(state):
    url = f'{CONTROL_SERVER_URL}/compressor'
    resp = requests.post(url, json={'value': state})
    print(resp.text)

def set_pressure_threshold(threshold):
    url = f'{CONTROL_SERVER_URL}/pressure-threshold'
    resp = requests.post(url, json={'threshold': threshold})
    print(resp.text)

def set_lower_pressure_threshold(threshold):
    url = f'{CONTROL_SERVER_URL}/lower-pressure-threshold'
    resp = requests.post(url, json={'threshold': threshold})
    print(resp.text)

def set_toggle_range(state, valve_index):
    url = f'{CONTROL_SERVER_URL}/toggle-range'
    payload = {'state': state}
    if valve_index is not None:
        payload['valveIndex'] = valve_index
    resp = requests.post(url, json=payload)
    print(resp.text)

def get_status():
    url = f'{CONTROL_SERVER_URL}/status'
    resp = requests.get(url)
    print(resp.text)

def connect_pi(pi_ip):
    url = f'{CONTROL_SERVER_URL}/connect-pi'
    resp = requests.post(url, json={'piIp': pi_ip})
    print(resp.text)

def main():
    parser = argparse.ArgumentParser(description='Control client for pipeline system.')
    subparsers = parser.add_subparsers(dest='command')

    parser_valve = subparsers.add_parser('valve', help='Toggle a valve')
    parser_valve.add_argument('index', type=int)
    parser_valve.add_argument('state', choices=['on', 'off'])

    parser_compressor = subparsers.add_parser('compressor', help='Toggle compressor')
    parser_compressor.add_argument('state', choices=['on', 'off'])

    parser_threshold = subparsers.add_parser('threshold', help='Set pressure threshold')
    parser_threshold.add_argument('value', type=float)

    parser_lower = subparsers.add_parser('lower-threshold', help='Set lower pressure threshold')
    parser_lower.add_argument('value', type=float)

    parser_toggle = subparsers.add_parser('toggle-range', help='Toggle automatic compress/release')
    parser_toggle.add_argument('state', choices=['on', 'off'])
    parser_toggle.add_argument('--valve', type=int, help='Valve index (optional)')

    parser_status = subparsers.add_parser('status', help='Get system status')

    parser_connect = subparsers.add_parser('connect-pi', help='Connect to Raspberry Pi')
    parser_connect.add_argument('ip', type=str)

    args = parser.parse_args()

    if args.command == 'valve':
        set_valve(args.index, args.state == 'on')
    elif args.command == 'compressor':
        set_compressor(args.state == 'on')
    elif args.command == 'threshold':
        set_pressure_threshold(args.value)
    elif args.command == 'lower-threshold':
        set_lower_pressure_threshold(args.value)
    elif args.command == 'toggle-range':
        set_toggle_range(args.state, args.valve)
    elif args.command == 'status':
        get_status()
    elif args.command == 'connect-pi':
        connect_pi(args.ip)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
