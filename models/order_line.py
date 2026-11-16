from odoo import fields, models

class OrderLine(models.Model):
    """One work item of a repair order."""

    _name='fixit.order.line'
    _description = 'Order line of Fixit'

    name = fields.Char(string='Name')
    order_id = fields.Many2one(string='Order ID', comodel_name="fixit.order")