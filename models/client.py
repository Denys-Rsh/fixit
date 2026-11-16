from odoo import fields, models

class Client(models.Model):
    """Client of the service center (extends res.partner)."""

    _inherit='res.partner'
    _description = 'Client of Fixit'

    name = fields.Char(string='Name')