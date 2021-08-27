# -*- coding: utf-8 -*-

{% for module in sub_modules %}
from . import {{ module }}
{%- endfor %}

