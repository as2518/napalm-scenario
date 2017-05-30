import sys
import yaml
from pprint import pprint, pformat
from argparse import ArgumentParser
import time

# clolor font
import colorama
from colorama import Fore, Back, Style

from router import Router

def print_bool_result(binary_result,color_spec):
    """ 
    print boolean result.
    @params:
        binary_result - Required : Ture or False boolean 
        color_spec    - Required : specifid colorama option. e.g. 'Back','Fore'
    """
    if binary_result:
        print(eval(color_spec).GREEN + '[OK]' , end=' ')
    else:
        print(eval(color_spec).RED + '[NG]' , end=' ')

def print_validate_fail_detail(compare_object,key=''):
    """
    print invalid reason.
    @params:
        compare_object - Required : validation result object (result of compliace_report())
        key            - Optional : dict key of compliance_result
    """
    if isinstance(compare_object,dict):
        for key,dst in compare_object.items():
            if isinstance(dst,dict):
                # recursive
                reason,result = print_validate_fail_detail(dst,key)
                if not reason == None:
                    print(' '*9 , end='')
                    print(Fore.RED + 'INVALID! [type:{0}] {1} : {2}'.format(key,reason,result))
            elif isinstance(dst,list):
                for d in dst:
                    return key,d
            elif isinstance(dst,int):
                if not (isinstance(dst,bool)) or (key == 'actual_value'):
                    return key,dst
    return None,None


def input_judgment(message): 
    print(Fore.YELLOW + message, end = '(y/n): ')
    choice = input().lower()
    if choice == 'y':
        return True
    else:
        return False

def rollback_operation(device,config):
    try:
        replace_result = device.replace(config)
        device_result = device.commit()
        rollback = replace_result & commit_result
        print_bool_result(rollback,'Fore')
        print('Rollbacked config!')

    except Exception as err:
        print(Back.RED + 'Rollback Error!!')
        print(Back.RED + str(err))

    finally:
        router1.close()
        sys.exit()

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
        os          = param['hosts']['os'],
        ipaddress   = param['hosts']['management_ipaddress'],
        username    = param['hosts']['username'],
        password    = param['hosts']['password'])

    print('########## Run Senario : ' + args.file + ' ##########')

    print('operator : %s'       % (param['operator']))
    print('operation_date : %d' % (param['operation_date']))
    print('hostname : %s'       % (param['hosts']['hostname']))
    print('purpose :')
    print(param['purpus'])
    
    print('Connect to ' + param['hosts']['hostname'] + ' : ', end='')
    test = router1.open()
    print(test)
    print(Fore.GREEN + 'OK')

    backup_configs = router.get_config()
    if backup_configs:
        print_bool_result(True,'Fore')
    else:
        print_bool_result(False,'Fore')
    print('save backup config')

    for scenario_param in param['scenario']:
        if isinstance(scenario_param, dict):
            operation_name  = next(iter(scenario_param))
            operation_param = scenario_param[operation_name]
        else:
            operation_name = scenario_param
            operation_param = None

        if 'validate' == operation_name:
            print(Fore.BLUE+'Pre-Validation Start : {0}'.center(50,'=').format(param['hosts']['hostname']))
            if operation_param:
                complies_result = router1.validate_operation(operation_param)
            else:
                complies_result = router1.validate_operation({operation_name:None})

            #pprint(complies_result)

            print_bool_result(complies_result['complies'],'Back')
            print('Validation total result')
            v_index = complies_result.keys()
            for v in v_index:
                if v.startswith('get_'):
                    print(' '*4 , end='')
                    print_bool_result(complies_result[v]['complies'],'Fore')
                    print('validate {0}'.format(v))
                    if not complies_result[v]['complies']:
                        print_validate_fail_detail(complies_result[v])
            if not complies_result['complies']:
                if not input_judgment('Validate is fail. Continue?'):
                    rollback_operation(router1,backup_config)

        elif 'get_' in operation_name:
            print(Fore.BLUE+'Get and show command : {0}'.center(50,'=').format(param['hosts']['hostname']))
            print('GET <%s> : '%(operation_name))
            result = router1.call_getters(operation_name,operation_param)
            pprint(result)

        elif 'set_' in operation_name:
            print(Fore.BLUE+'Set Config : {0}'.center(50,'=').format(param['hosts']['hostname']))  
            result, message =\
                router1.load_config(operation_name, operation_param)
            print_bool_result(result,'Fore')
            print('Load config on < {0} > '.format(operation_name))
            if result:
                print('-'*30)
                print(Fore.YELLOW + message)
                print('-'*30)
            else:
                print(Back.RED + message)
                print(Back.RED + 'Config load error! system exit.')
                rollback_operation(router1,backup_configs['running'])
                router1.close()
                sys.exit()
            
            print(Fore.BLUE+'Compare Config : {0}'.center(50,'=').format(param['hosts']['hostname']))
            print('Compare config on < {0} >'.format(operation_name))
            message = router1.compare_config()
            if message != '':
                print('-'*50)
                print(Fore.YELLOW + message)
                print('-'*50)
                if input_judgment('Do you commit?'):
                    print_bool_result(router1.commit(),'Fore')
                    print('Commit config')
                else:

            else:
                print(Fore.YELLOW+'[INFO] No changes this router by {0} config'.format(operation_name))

        elif operation_name == 'sleep_10sec':
            print('Sleep 10 sec : ', end='')
            time.sleep(10)
            print(Fore.GREEN + 'OK')

        else:
            print('Cannnot run operation : '+Back.RED + operation_name)

    print('Close the connection to ' + param['hosts']['hostname'])
    router1.close()

    print(Fore.BLUE+'########## End Senario : ' + args.file + ' ##########')

if __name__ == '__main__':
    main()