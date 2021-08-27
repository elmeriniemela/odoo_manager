# -*- coding: utf-8 -*-
{
    'name': '{{ Title(module_name) }}',
    'version': '1.0',
    'license': 'Other proprietary',
    'category': 'General',
    'author': 'SprintIT Oy, {{ author }}',
    'maintainer': 'SprintIT Oy, {{ author }}',
    'website': 'http://www.sprintit.fi',
    'depends': [
        {%- for dependency in depends %}
        '{{ dependency }}',
        {%- endfor %}
    ],
    'data': [
        'security/ir.model.access.csv',
        {%- for view in views %}
        'views/{{ view.replace('.', '_') }}_view.xml',
        {%- endfor %}
    ],
    'demo': [
    ],
    'test': [
    ],
    "external_dependencies": { # python pip packages
    #     'python': ['suds', 'dateutil'],
    },
    'installable': True,
    'auto_install': False,
 }
