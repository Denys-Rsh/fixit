from datetime import timedelta

from odoo import fields, models
from odoo.exceptions import UserError


class OrderReportWizard(models.TransientModel):
    _name = 'fixit.order.report.wizard'
    _description = 'Orders report wizard'

    order_ids = fields.Many2many(
        comodel_name='fixit.order',
        string='Orders',
        default=lambda self: self._default_active_ids('fixit.order'),
    )
    repairman_ids = fields.Many2many(
        comodel_name='res.users',
        string='Repairmen',
        default=lambda self: self._default_active_ids('res.users'),
    )
    date_from = fields.Date(string='Period Start')
    date_to = fields.Date(string='Period End')

    def _default_active_ids(self, model_name):
        """Records selected in the list of model_name become the default value."""
        if self.env.context.get('active_model') == model_name:
            return self.env.context.get('active_ids')
        return False

    def action_show_report(self):
        """Print the PDF report for the orders matching the wizard fields."""
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise UserError('The period start cannot be later than the period end.')

        domain = []
        if self.order_ids:
            domain.append(('id', 'in', self.order_ids.ids))
        if self.repairman_ids:
            domain.append(('repairman_id', 'in', self.repairman_ids.ids))
        if self.date_from:
            domain.append(('create_date', '>=', self.date_from))
        if self.date_to:
            # create_date is a datetime, so include the whole last day
            domain.append(('create_date', '<', self.date_to + timedelta(days=1)))

        orders = self.env['fixit.order'].search(domain)
        if not orders:
            raise UserError('No orders found for these filters.')
        return self.env.ref('fixit.fixit_order_report').report_action(orders)
