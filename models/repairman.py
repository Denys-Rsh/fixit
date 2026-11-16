from odoo import fields, models

class Repairman(models.Model):
    """Repairman who is assigned to orders (extends res.users)."""

    _inherit = 'res.users'
    _description = 'Repairman of Fixit'

    name = fields.Char(string='Name')