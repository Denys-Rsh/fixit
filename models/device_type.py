from odoo import fields, models


class DeviceType(models.Model):
    """Kind of equipment: laptop, phone, printer..."""

    _name = 'fixit.device.type'
    _description = 'Device type'

    name = fields.Char(string='Name', required=True)
    warranty_months = fields.Integer(string='Warranty (months)', default=3)
