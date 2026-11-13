from odoo import fields, models

class Repairman(models.Model):
    _inherit = 'res.users'
    _description = 'Repairman of Fixit'

    name = fields.Char(string='Name')