# -*- coding: utf-8 -*-

import logging
log = logging.getLogger(__name__)

from odoo import models, fields, api

class {{ ModelName }}(models.TransientModel):
    _inherit = "{{ dot_model_temp_name }}"
