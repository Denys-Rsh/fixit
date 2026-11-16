from odoo import fields, models

class Part(models.Model):
    """Spare part that can be used in a repair."""

    _name='fixit.part'
    _description = 'Device part'

    name = fields.Char(string='Name')
    price = fields.Float(string='Price')