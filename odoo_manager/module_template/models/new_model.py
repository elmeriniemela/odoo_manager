# -*- coding: utf-8 -*-

# Standard library imports
import logging

# External library imports
# import requests

# Odoo imports
from odoo import models, fields, api

#Relative imports
# from . import xyz

_logger = logging.getLogger(__name__)


class {{ ModelName(model) }}(models.Model):
    _name = "{{ model }}"
    _inherit = ['mail.thread']
    _description = "{{ Title(model) }}"

    name = fields.Char(required=True)

