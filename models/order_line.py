from odoo import api, fields, models


class OrderLine(models.Model):
    """One work item of a repair order."""

    _name = 'fixit.order.line'
    _description = 'Order line of Fixit'

    name = fields.Char(string='Description', required=True)
    order_id = fields.Many2one(comodel_name='fixit.order', string='Order', required=True, ondelete='cascade')
    part_id = fields.Many2one(comodel_name='fixit.part', string='Part')
    quantity = fields.Float(string='Quantity', default=1)
    price = fields.Float(string='Price')
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal')

    @api.onchange('part_id')
    def _onchange_part_id(self):
        self.price = self.part_id.price

    @api.depends('quantity', 'price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price
