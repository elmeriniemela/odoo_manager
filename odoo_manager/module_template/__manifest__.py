# -*- coding: utf-8 -*-
{
    'name': '{{ title_name }}',
    'version': '0.1',
    'license': 'Other proprietary',
    'category': 'General',
    'author': 'SprintIT, {{ author }}',
    'maintainer': 'SprintIT, {{ author }}',
    'website': 'http://www.sprintit.fi',
    'depends': [
        {% for dependency in depends %}
        '{{ dependency }}',
        {% endfor %}
    ],
    'data': [
        {% for view in views %}
        'views/{{ view }}',
        {% endfor %}
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
