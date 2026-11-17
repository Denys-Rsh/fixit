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

    _check_quantity = models.Constraint('CHECK(quantity > 0)', 'Quantity must be positive.')

    @api.onchange('part_id')
    def _onchange_part_id(self):
        """Fill the price and description from the chosen part."""
        self.price = self.part_id.price
        if not self.name:
            self.name = self.part_id.name

    @api.depends('quantity', 'price')
    def _compute_subtotal(self):
        """Subtotal of the line is quantity * price."""
        for line in self:
            line.subtotal = line.quantity * line.price
