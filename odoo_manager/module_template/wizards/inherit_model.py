# -*- coding: utf-8 -*-

import logging
log = logging.getLogger(__name__)

from odoo import models, fields, api

class {{ ModelName(model) }}(models.TransientModel):
    _inherit = "{{ model }}"

