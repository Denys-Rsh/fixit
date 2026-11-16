from odoo import fields, models


class MassReassignRepairmanWizard(models.TransientModel):
    """Assign one repairman to many orders selected in the list."""

    _name = 'fixit.mass.reassign.repairman.wizard'
    _description = 'Mass reassign repairman wizard'

    order_ids = fields.Many2many(
        comodel_name='fixit.order',
        string='Orders',
        # Orders selected in the list come through active_ids
        default=lambda self: self.env.context.get('active_ids'),
    )
    repairman_id = fields.Many2one(comodel_name='res.users', string='New Repairman', required=True)

    def action_reassign(self):
        """Write the chosen repairman to all selected orders."""
        self.order_ids.write({'repairman_id': self.repairman_id.id})
