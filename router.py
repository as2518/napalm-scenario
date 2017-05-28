# Jinja2 Template Engine
from jinja2 import Template, Environment
import napalm
# arranged print
from pprint import pprint, pformat

#Define Const
VALIDATE_TEMPLATE_PATH = './validate_templates/validate_'
VALIDATE_RULE_PATH = './validate_rules'
INTERFACE = 'interface'


class Router:
    def __init__(self, hostname, os, ipaddress, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.ipaddress = ipaddress
        self.os = os
        self.driver = napalm.get_network_driver(self.os)
        self.device = self.driver(hostname=ipaddress, username=username, password=password)


    def open(self):
        self.device.open()


    def close(self):
        self.device.close()


    def commit(self):
        return self.device.commit_config()


    def discard_config(self):
        return self.device.discard_config()


    def compare_config(self):
        return self.device.compare_config()


    def check_hostname(self):
        hostname_fetched = self.device.get_facts()['hostname']

        if hostname_fetched == self.hostname :
            return True, hostname_fetched
        else:
            return False, hostname_fetched


    def call_getters(self,func_name):
        return eval('self.device.'+func_name)()


    def load_config(self, operation_name, operation_param=None):
        result = False
        message = ''

        if operation_name == 'set_add_interface_ipv4':
            template_filename = './set_templates/' + self.os + '/add_interface_ipv4.j2'
            template_param = operation_param
        elif operation_name == 'set_add_network_ipv4':
            template_filename = './set_templates/' + self.os + '/add_network_ipv4.j2'
            template_param = operation_param
        elif operation_name == 'set_add_bgp_neighbor_ipv4':
            template_filename = './set_templates/' + self.os + '/add_bgp_neighbor_ipv4.j2'
            template_param = operation_param
        elif operation_name == 'set_add_bgp_policy_ipv4':
            template_filename = './set_templates/' + self.os + '/add_bgp_policy_ipv4.j2'
            template_param = operation_param
        else:
            pass

        try:
            # This is only brawsing for check candidate configuration before setting the router.
            config_txt = self.generate_from_jinja2(
                template_filename,
                template_param)
            #print(config_txt) #debug point
            self.device.load_merge_candidate(config=config_txt)
            #TODO: you can use load_template() instead of load_merge_candidate().

            message = config_txt
            result = True
        except Exception as err:
            result = False
            print ("Error : "+str(err))
            message= str(err)
        return result, message


    def validate_operation(self, validate_dst):
        base_str = ''
        for validate_oper in validate_dst:
            if isinstance(validate_oper,dict):
                validate_filename = list(validate_oper.keys())[0]
            else:
                validate_filename = validate_oper
            rule_path=VALIDATE_TEMPLATE_PATH+validate_filename+'.j2'
            temp_param = self.allocate_validation_param(validate_filename,validate_oper)
            base_str += self.generate_from_jinja2(rule_path,temp_param)
        yml_path = self.save_as_yml(base_str,VALIDATE_RULE_PATH)
        return self.device.compliance_report(yml_path)


    def allocate_validation_param(self,oper_name ,oper_dict):
        if oper_name in 'interfaces':
            ifvalid_list = {'interfaces':{}}
            facts_result = self.call_getters('get_facts')
            ifvalid_list['interfaces']['interfaces_name'] = facts_result['interface_list']
            return ifvalid_list

        elif oper_name in 'environment':
            env_result = self.call_getters('get_environment')
            for v_order in oper_dict[oper_name].keys():
                if v_order in 'cpu':
                    pass
                if v_order in 'memory':
                    pass
            return env_result 

        else:
            return oper_dict
        

    def save_as_yml(self,yml_data,save_dir):
        save_filepath = save_dir+'/validate_rule.yml'
        with open(save_filepath, 'w') as f:
            f.write(yml_data)
            f.close
        return save_filepath
    
    def generate_from_jinja2(self, template_filename, template_param):
        # read template file (jinja2 format)
        with open(template_filename, 'r') as f:
            template_jinja2 = f.read()

        # generate nwtest file from template file
        return Environment().from_string(template_jinja2).render(template_param)
        