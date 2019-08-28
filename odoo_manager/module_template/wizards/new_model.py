# -*- coding: utf-8 -*-

# Standard library imports
import logging

# External library imports
# import requests

# Odoo imports
from odoo import models, fields, api

#Relative imports
# from . import xyz

log = logging.getLogger(__name__)


class {{ ModelName(model) }}(models.TransientModel):
    _name = "{{ model }}"
    _description = "{{ Title(model) }}"
