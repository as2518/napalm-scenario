#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Jinja2 Template Engine
from jinja2 import Template, Environment

## PyEZ
#from jnpr.junos import Device
#from jnpr.junos.utils.config import Config

## JSNAPy
#from jnpr.jsnapy import SnapAdmin

import napalm

# arranged print
from pprint import pprint, pformat


class Router:
    def __init__(self, hostname, model, os, ipaddress, username, password):
        self.hostname = hostname
        self.model = model
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

    def rollback(self):

        self.device.discard_config()

    def compare_config(self):
        return self.device.compare_config()

    def load_config(self, operation_name, operation_param=None):
        # PyEZ function

        '''
        set_result = False
        message = ''
        if operation_name == 'set_add_interface':
            template_filename = './set_templates/add_interface.jinja2'
            tamplate_param = operation_param
        elif operation_name == 'set_add_bgp_neighbor':
            template_filename = './set_templates/add_bgp_neighbor.jinja2'
            tamplate_param = operation_param
        elif operation_name == 'set_add_bgp_policy_external':
            template_filename =\
                './set_templates/add_bgp_policy_external.jinja2'
            tamplate_param = operation_param
        else:
            pass

        config_txt = self.generate_from_jinja2(
            template_filename,
            tamplate_param)

        self.device.cu.load(
            template_path=template_filename,
            template_vars=tamplate_param,
            format="text",
            merge=True)

        message = config_txt
        set_result = True

        return set_result, message
        '''
        pass

    def nwtest(self, operation_name, operation_param=None):
        # PyEZ function

        '''
        nwtest_result = False
        message = ''
        template_filename = ''

        if operation_name == 'nwtest_hostname':
            template_filename =\
                './nwtest_templates/%s.jinja2' % (operation_name)
            tamplate_param = {'hostname': self.hostname}
            nwtest_filename =\
                './nwtests/' +\
                operation_name + '_' +\
                self.hostname +\
                '.yml'

        elif operation_name == 'nwtest_model':
            template_filename =\
                './nwtest_templates/%s.jinja2' % (operation_name)
            tamplate_param = {'model': self.model}
            nwtest_filename =\
                './nwtests/' +\
                operation_name + '_' +\
                self.hostname +\
                '.yml'

        elif operation_name == 'nwtest_interface':
            template_filename =\
                './nwtest_templates/%s.jinja2' % (operation_name)
            tamplate_param = operation_param
            nwtest_filename =\
                './nwtests/' +\
                operation_name + '_' +\
                operation_param['interface_name'].replace('/', '-') + '_' +\
                operation_param['interface_status'] +\
                '.yml'

        elif operation_name == 'nwtest_bgp_neighbor':
            template_filename =\
                './nwtest_templates/%s.jinja2' % (operation_name)
            tamplate_param = operation_param
            nwtest_filename =\
                './nwtests/' +\
                operation_name + '_' +\
                operation_param['neighbor_address_ipv4'].replace('.', '-') + '_' +\
                operation_param['neighbor_status'] +\
                '.yml'

        elif operation_name == 'nwtest_bgp_received_route':
            template_filename =\
                './nwtest_templates/%s.jinja2' % (operation_name)
            tamplate_param = operation_param
            nwtest_filename =\
                './nwtests/' +\
                operation_name + '_' +\
                operation_param['neighbor_address_ipv4'].replace('.', '-') + '_' +\
                operation_param['received_route_address_ipv4'].replace('.', '-') +\
                '.yml'

        elif operation_name == 'nwtest_bgp_advertised_route':
            template_filename =\
                './nwtest_templates/%s.jinja2' % (operation_name)
            tamplate_param = operation_param
            nwtest_filename =\
                './nwtests/' +\
                operation_name + '_' +\
                operation_param['neighbor_address_ipv4'].replace('.', '-') + '_' +\
                operation_param['advertised_route_address_ipv4'].replace('.', '-') +\
                '.yml'

        elif operation_name == 'nwtest_ping':
            template_filename =\
                './nwtest_templates/%s.jinja2' % (operation_name)
            tamplate_param = operation_param
            nwtest_filename =\
                './nwtests/' +\
                operation_name + '_' +\
                operation_param['target_ipaddress'].replace('.', '-') +\
                '.yml'

        else:
            pass

        self.generate_nwtestfile(
            template_filename=template_filename,
            template_param=tamplate_param,
            nwtest_filename=nwtest_filename)

        jsnapy_conf = 'nwtests:' + '\n' +\
                      '  - %s' % (nwtest_filename)

        snapcheck_dict = self.snap.snapcheck(data=jsnapy_conf, dev=self.device)

        for snapcheck in snapcheck_dict:
            if snapcheck.result == 'Passed':
                nwtest_result = True

                if operation_name == 'nwtest_bgp_received_route':
                    expected_value = '%s/%s' % (
                        operation_param['received_route_address_ipv4'],
                        operation_param['received_route_subnet_ipv4'])
                    acutual_value =\
                        snapcheck.test_details.values()[0][0]['passed'][0]['pre'].keys()[0]

                elif operation_name == 'nwtest_bgp_advertised_route':
                    expected_value = '%s/%s' % (
                        operation_param['advertised_route_address_ipv4'],
                        operation_param['advertised_route_subnet_ipv4'])
                    acutual_value =\
                        snapcheck.test_details.values()[0][0]['passed'][0]['pre'].keys()[0]

                else:
                    expected_value =\
                        snapcheck.test_details.values()[0][0]['expected_node_value']
                    acutual_value =\
                        snapcheck.test_details.values()[0][0]['passed'][0]['actual_node_value']

                message =\
                    'nwtest file      : %s\n' % nwtest_filename +\
                    'expected value : %s\n' % (expected_value) +\
                    'acutual  value : %s' % (acutual_value)

            elif snapcheck.result == 'Failed':
                nwtest_result = False

                if operation_name == 'nwtest_bgp_received_route':
                    expected_value = '%s/%s' % (
                        operation_param['received_route_address_ipv4'],
                        operation_param['received_route_subnet_ipv4'])
                    acutual_value = 'None'

                elif operation_name == 'nwtest_bgp_advertised_route':
                    expected_value = '%s/%s' % (
                        operation_param['advertised_route_address_ipv4'],
                        operation_param['advertised_route_subnet_ipv4'])
                    acutual_value = 'None'

                else:
                    expected_value =\
                        snapcheck.test_details.values()[0][0]['expected_node_value']
                    acutual_value =\
                        snapcheck.test_details.values()[0][0]['failed'][0]['actual_node_value']

                message = 'nwtest file      : %s\n' % nwtest_filename +\
                    'expected value : %s\n' % (expected_value) +\
                    'acutual  value : %s' % (acutual_value)

        return nwtest_result, message
        '''
        pass

    def generate_nwtestfile(self, template_filename, template_param, nwtest_filename):
        '''
        nwtest_yml = self.generate_from_jinja2(template_filename, template_param)
        # write nwtest file (YAML format)
        with open(nwtest_filename, 'w') as f:
            f.write(nwtest_yml)
        '''
        pass
    def generate_from_jinja2(self, template_filename, template_param):
        '''
        # read template file (jinja2 format)
        with open(template_filename, 'r') as f:
            template_jinja2 = f.read()

        # generate nwtest file from template file
        return Environment().from_string(template_jinja2).render(template_param)
        '''
        pass
