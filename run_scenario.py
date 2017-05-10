#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import yaml
from pprint import pprint, pformat
from argparse import ArgumentParser
import time

# clolor font
import colorama
from colorama import Fore, Back, Style

from router import Router

def main():
    """main function."""

    # Parse argment
    parser = ArgumentParser(description='run scenario_file')
    parser.add_argument('-f', '--file',
                        type=str,
                        help='scenario file',
                        required=True)
    args = parser.parse_args()

    # Set color font
    colorama.init(autoreset=True)

    # Read router infomation file
    try:
        with open(args.file, 'r') as f:
            param_yaml = f.read()
    except (IOError, IndexError):
        sys.stderr.write('Cannot open file : ' + args.file + '\n')
        sys.exit(1)

    # Convert yaml format to python_type
    try:
        param = yaml.load(param_yaml)
    except ValueError as error:
        sys.stderr.write('YAML format error : \n')
        sys.stderr.write(param_yaml)
        sys.stderr.write(str(error))
        sys.exit(1)

    router1 = Router(
        hostname    = param['hosts']['hostname'],
        model       = param['hosts']['model'],
        os          = param['hosts']['os'],
        ipaddress   = param['hosts']['management_ipaddress'],
        username    = param['hosts']['username'],
        password    = param['hosts']['password'])

    print('########## Run Senario : ' + args.file + ' ##########')

    print('operator : %s'       % (param['operator']))
    print('operation_date : %d' % (param['operation_date']))
    print('hostname : %s'       % (param['hosts']['hostname']))
    print('model : %s'          % (param['hosts']['model']))
    print('purpose :')
    print(param['purpus'])
    
    print('Connect to ' + param['hosts']['hostname'] + ' : ', end='')
    router1.open()
    print(Fore.GREEN + 'OK')

    for scenario_param in param['scenario']:
        if isinstance(scenario_param, dict):
            operation_name  = scenario_param.keys()[0]
            operation_param = scenario_param[operation_name]
        else:
            operation_name = scenario_param
            operation_param = None

        if 'nwtest_' in operation_name:
            print('Test on < %s > : ' % (operation_name), end='')
            result, message =\
                router1.snaptest(operation_name, operation_param)

            if result:
                print(Fore.GREEN + 'OK')
                print(Fore.GREEN + message)
            else:
                print(Fore.RED + 'NG')
                print(Fore.RED + message)

        elif 'set_' in operation_name:
            print('Load config on < %s > : ' % (operation_name), end='')
            result, message =\
                router1.load_config(operation_name, operation_param)
            if result:
                print(Fore.GREEN + 'OK')
                print('-'*30)
                print('Set config: ')
                print('-'*30)
                print(Fore.YELLOW + message)
                print('-'*30)
            else:
                print(Fore.RED + 'NG')
                print(Fore.RED + message)

            print('Diff config :')
            message = router1.diff_config()
            print('-'*30)
            print(Fore.YELLOW + message)
            print('-'*30)

            print('Commit Check : ', end='')
            if router1.commit_check():
                print(Fore.GREEN + 'OK')
            else:
                print(Fore.RED + 'NG')

            print(Fore.YELLOW + "Do you commit? y/n")
            choice = raw_input().lower()
            if choice == 'y':
                print('Commit : ', end='')
                if router1.commit():
                    print(Fore.GREEN + 'OK')
                else:
                    print(Fore.RED + 'NG')
            else:
                print('Rollback : ', end='')
                if router1.rollback():
                    print(Fore.GREEN + 'OK')
                else:
                    print(Fore.RED + 'NG')

        elif operation_name == 'sleep_10sec':
            print('sleep 10 sec : ', end='')
            time.sleep(10)
            print(Fore.GREEN + 'OK')

        else:
            print('Cannnot run operation : ' + operation_name)

    print('Close the connection to ' + param['hosts']['hostname'] + ' : ', end='')
    router1.close()
    print(Fore.GREEN + 'OK')

    print('########## End Senario : ' + args.file + ' ##########')

if __name__ == '__main__':
    main()