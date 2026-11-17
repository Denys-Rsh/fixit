from odoo import fields, models


class Client(models.Model):
    """Client of the service center (extends res.partner)."""

    _inherit = 'res.partner'

    fixit_device_ids = fields.One2many(comodel_name='fixit.device', inverse_name='client_id', string='Devices')
