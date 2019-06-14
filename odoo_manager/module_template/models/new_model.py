# -*- coding: utf-8 -*-

import logging
log = logging.getLogger(__name__)

from odoo import models, fields, api

class {{ ModelName(model) }}(models.Model):
    _name = "{{ model }}"
    _inherit = ['mail.thread']
    _description = "{{ Title(model) }}"

    name = fields.Char(required=True)

