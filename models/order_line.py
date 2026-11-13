from odoo import fields, models

class OrderLine(models.Model):
    _name='fixit.order.line'
    _description = 'Order line of Fixit'

    name = fields.Char(string='Name')
    order_id = fields.Many2one(string='Order ID', comodel_name="fixit.order")