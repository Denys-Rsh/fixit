from odoo import fields, models


class Device(models.Model):
    """A device that a client brings for repair."""

    _name = 'fixit.device'
    _description = 'Client device'

    name = fields.Char(string='Model', required=True)
    serial_number = fields.Char(string='Serial Number')
    device_type_id = fields.Many2one(comodel_name='fixit.device.type', string='Device Type')
    client_id = fields.Many2one(comodel_name='res.partner', string='Owner')
