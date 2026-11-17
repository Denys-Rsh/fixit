from odoo import api, fields, models
from odoo.exceptions import UserError

# Where an order can go from each state. Picked Up and Cancelled are final.
NEXT_STATES = {
    'new_request': ['diagnostics', 'cancelled'],
    'diagnostics': ['customer_approval', 'cancelled'],
    'customer_approval': ['awaiting', 'in_repair', 'cancelled'],
    'awaiting': ['in_repair', 'cancelled'],
    'in_repair': ['ready', 'cancelled'],
    'ready': ['picked_up'],
    'picked_up': [],
    'cancelled': [],
}


class Order(models.Model):
    """Repair order: a device brought by a client and fixed by a repairman."""

    _name = 'fixit.order'
    _description = 'Order of Fixit'

    name = fields.Char(string='Name', required=True)
    state = fields.Selection([
        ('new_request', 'New Request'),
        ('diagnostics', 'Diagnostics'),
        ('customer_approval', 'Customer Approval'),
        ('awaiting', 'Awaiting Parts'),
        ('in_repair', 'In Repair'),
        ('ready', 'Ready'),
        ('picked_up', 'Picked Up'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='new_request', readonly=True)
    client_id = fields.Many2one(comodel_name='res.partner', string='Client')
    device_id = fields.Many2one(comodel_name='fixit.device', string='Device')
    repairman_id = fields.Many2one(comodel_name='res.users', string='Repairman')
    line_ids = fields.One2many(comodel_name='fixit.order.line', inverse_name='order_id', string='Works')
    amount_total = fields.Float(string='Total', compute='_compute_amount_total')

    @api.depends('line_ids.subtotal')
    def _compute_amount_total(self):
        """Total of the order is the sum of its line subtotals."""
        for order in self:
            order.amount_total = sum(order.line_ids.mapped('subtotal'))

    def _set_state(self, new_state):
        """Change the state only if NEXT_STATES allows it."""
        for order in self:
            if new_state not in NEXT_STATES[order.state]:
                raise UserError(self.env._('This order cannot go to this status now.'))
            order.state = new_state

    def action_diagnostics(self):
        """Move the order to Diagnostics."""
        self._set_state('diagnostics')

    def action_approval(self):
        """Move the order to Customer Approval."""
        self._set_state('customer_approval')

    def action_awaiting(self):
        """Move the order to Awaiting Parts."""
        self._set_state('awaiting')

    def action_repair(self):
        """Move the order to In Repair."""
        self._set_state('in_repair')

    def action_ready(self):
        """Move the order to Ready."""
        self._set_state('ready')

    def action_picked_up(self):
        """Move the order to Picked Up."""
        self._set_state('picked_up')

    def action_cancel(self):
        """Cancel the order."""
        self._set_state('cancelled')
