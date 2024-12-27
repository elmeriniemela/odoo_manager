# -*- coding: utf-8 -*-
{
    'name': '{{ Title(module_name) }}',
    'version': '1.0',
    'license': 'Other proprietary',
    'category': 'General',
    'author': 'SprintIT Oy',
    'maintainer': 'SprintIT Oy',
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
    'installable': True,
    'auto_install': False,
 }
