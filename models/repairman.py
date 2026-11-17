from odoo import fields, models


class Repairman(models.Model):
    """Repairman who is assigned to orders (extends res.users)."""

    _inherit = 'res.users'

    fixit_order_ids = fields.One2many(comodel_name='fixit.order', inverse_name='repairman_id', string='Repair Orders')
