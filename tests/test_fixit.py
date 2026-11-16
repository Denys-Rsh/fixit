from datetime import date

from odoo.exceptions import AccessError, UserError
from odoo.tests import TransactionCase, new_test_user, tagged


@tagged('post_install', '-at_install')
class TestFixit(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Internal user (base.group_user) has access through ir.model.access.csv
        cls.user = new_test_user(cls.env, login='fixit_user', groups='base.group_user')
        # Portal user is not in base.group_user, so has no access
        cls.portal = new_test_user(cls.env, login='fixit_portal', groups='base.group_portal')
        cls.repairman = new_test_user(cls.env, login='fixit_repairman', groups='base.group_user')

    # ---------- fixit.order ----------

    def test_order_access(self):
        order = self.env['fixit.order'].with_user(self.user).create({'name': 'Phone'})
        self.assertEqual(order.create_uid, self.user)

        with self.assertRaises(AccessError) as error:
            self.env['fixit.order'].with_user(self.portal).create({'name': 'Phone'})
        self.assertIn('(fixit.order)', str(error.exception))

    # ---------- fixit.order.line ----------

    def test_order_line_access(self):
        order = self.env['fixit.order'].with_user(self.user).create({
            'name': 'Laptop',
            'line_ids': [(0, 0, {'name': 'Change screen'})],
        })
        self.assertEqual(order.line_ids.order_id, order)

        with self.assertRaises(AccessError) as error:
            order.line_ids.with_user(self.portal).read(['name'])
        self.assertIn('(fixit.order.line)', str(error.exception))

    # ---------- fixit.part ----------

    def test_part_access(self):
        part = self.env['fixit.part'].with_user(self.user).create({'name': 'Battery', 'price': 500})
        part.write({'price': 450})
        self.assertEqual(part.price, 450)

        with self.assertRaises(AccessError) as error:
            self.env['fixit.part'].with_user(self.portal).search([])
        self.assertIn('(fixit.part)', str(error.exception))

    # ---------- fixit.mass.reassign.repairman.wizard ----------

    def test_mass_reassign_repairman(self):
        orders = self.env['fixit.order'].create([{'name': 'Order 1'}, {'name': 'Order 2'}])
        other_order = self.env['fixit.order'].create({'name': 'Order 3'})

        # Orders selected in the list come to the wizard through active_ids
        wizard = self.env['fixit.mass.reassign.repairman.wizard'].with_user(self.user).with_context(
            active_ids=orders.ids,
        ).create({'repairman_id': self.repairman.id})
        self.assertEqual(wizard.order_ids, orders)

        wizard.action_reassign()
        # Check each order: orders.repairman_id would pass even if only one was changed
        for order in orders:
            self.assertEqual(order.repairman_id, self.repairman)
        self.assertFalse(other_order.repairman_id)

    # ---------- fixit.order.report.wizard ----------

    def test_report_wizard_wrong_period(self):
        wizard = self.env['fixit.order.report.wizard'].create({
            'date_from': date(2026, 2, 1),
            'date_to': date(2026, 1, 1),
        })
        with self.assertRaises(UserError) as error:
            wizard.action_show_report()
        self.assertEqual(str(error.exception), 'The period start cannot be later than the period end.')

    def test_report_wizard_no_orders(self):
        wizard = self.env['fixit.order.report.wizard'].create({
            'date_from': date(2000, 1, 1),
            'date_to': date(2000, 1, 31),
        })
        with self.assertRaises(UserError) as error:
            wizard.action_show_report()
        self.assertEqual(str(error.exception), 'No orders found for these filters.')

    def test_report_wizard_filters_by_repairman(self):
        order = self.env['fixit.order'].create({'name': 'Mine', 'repairman_id': self.repairman.id})
        self.env['fixit.order'].create({'name': 'Not mine', 'repairman_id': self.user.id})

        # Repairmen selected in the users list become the wizard default
        wizard = self.env['fixit.order.report.wizard'].with_context(
            active_model='res.users',
            active_ids=self.repairman.ids,
            discard_logo_check=True,
        ).create({})
        self.assertEqual(wizard.repairman_ids, self.repairman)
        self.assertFalse(wizard.order_ids)

        action = wizard.action_show_report()
        self.assertEqual(action['context']['active_ids'], order.ids)
