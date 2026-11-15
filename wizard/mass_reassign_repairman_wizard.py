from odoo import fields, models


class MassReassignRepairmanWizard(models.TransientModel):
    _name = 'fixit.mass.reassign.repairman.wizard'
    _description = 'Mass reassign repairman wizard'

    order_ids = fields.Many2many(
        comodel_name='fixit.order',
        string='Orders',
        default=lambda self: self.env.context.get('active_ids'),
    )
    repairman_id = fields.Many2one(comodel_name='res.users', string='New Repairman', required=True)

    def action_reassign(self):
        self.order_ids.write({'repairman_id': self.repairman_id.id})
