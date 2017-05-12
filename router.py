#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Jinja2 Template Engine
from jinja2 import Template, Environment

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

    def load_config(self, operation_name, operation_param=None):
        result = False
        message = ''

        if operation_name == 'set_add_interface':
            template_filename = './set_templates/' + self.os + '/add_interface.j2'
            template_param = operation_param

        elif operation_name == 'set_add_bgp_neighbor':
            template_filename = './set_templates/' + self.os + '/add_bgp_neighbor.j2'
            template_param = operation_param

        elif operation_name == 'set_add_bgp_policy_external':
            template_filename = './set_templates/' + self.os + '/add_bgp_policy_external.jinja2'
            template_param = operation_param

        else:
            pass

        try:
            # This is only brawsing for check candidate configuration before setting the router.
            config_txt = self.generate_from_jinja2(
                template_filename,
                template_param)

            self.device.load_merge_candidate(config=config_txt)
            #TODO: you can use load_template() instead of load_merge_candidate().

            message = config_txt
            result = True
        except Exception as err:
            result = False
            print ("Error : "+str(err))
            message= str(err)

        return result, message


    def validate_operation(self, validation_name , validation_param=None):
        rule_filename = './validation_rules/validate-' + self.os + '.yml'
        result = self.device.compliance_report(rule_filename)

        return result

    def generate_from_jinja2(self, template_filename, template_param):
        # read template file (jinja2 format)
        with open(template_filename, 'r') as f:
            template_jinja2 = f.read()

        # generate nwtest file from template file
        return Environment().from_string(template_jinja2).render(template_param)
        