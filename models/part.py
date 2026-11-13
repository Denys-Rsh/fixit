from odoo import fields, models

class Client(models.Model):
    _name='fixit.part'
    _description = 'Device part'

    name = fields.Char(string='Name')
    price = fields.Float(string='Price')