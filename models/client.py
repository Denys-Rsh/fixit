from odoo import fields, models

class Client(models.Model):
    _inherit='res.partner'
    _description = 'Client of Fixit'

    name = fields.Char(string='Name')