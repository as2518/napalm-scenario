
#Define Const
VALIDATE_TEMPLATE_PATH = './validate_templates/validate_'
VALIDATE_RULE_PATH = './validate_rules'
VALIDATE_RULE_FILENAME = '/validate_rule.yml'

IF_PLEFIX_LIST = {
    'junos':[
        'fe-',# JUNOS
        'ge-',
        'xe-',
        'et-',
        'gr-',
        'gre',
        'lo',
        'ae'
    ],
    'iosxr':[
        'Fa',# IOSXR
        'Gi',
        'Te',
        'Fo',
        'Hu',
        'Eth',
        'Po',
        'Bu'
    ]
}

