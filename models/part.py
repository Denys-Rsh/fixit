from odoo import fields, models


class Part(models.Model):
    """Spare part that can be used in a repair."""

    _name = 'fixit.part'
    _description = 'Device part'

    name = fields.Char(string='Name', required=True)
    price = fields.Float(string='Price')
    device_type_id = fields.Many2one(comodel_name='fixit.device.type', string='Device Type')
