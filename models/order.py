from odoo import fields, models

class Order(models.Model):
    """Repair order: a device brought by a client and fixed by a repairman."""

    _name = 'fixit.order'
    _description = 'Order of Fixit'

    name = fields.Char(string='Name')
    state = fields.Selection([
        ('new_request', 'New Request'),
        ('diagnostics', 'Diagnostics'),
        ('awaiting', 'Awaiting'),
        ('customer_approval', 'Customer Approval'),
        ('in_repair', 'In Repair'),
        ('ready', 'Ready'),
        ('picked_up', 'Picked Up'),
        ('cancelled', 'Cancelled')
    ])
    line_ids = fields.One2many(comodel_name='fixit.order.line',inverse_name='order_id')
    repairman_id = fields.Many2one(comodel_name='res.users', string='Repairman')