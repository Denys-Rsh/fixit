from datetime import date

from psycopg2 import IntegrityError

from odoo.exceptions import AccessError, UserError
from odoo.tests import TransactionCase, new_test_user, tagged
from odoo.tools import mute_logger


@tagged('post_install', '-at_install')
class TestFixit(TransactionCase):
    """Access rights, record rules and wizards of the Fixit module."""

    @classmethod
    def setUpClass(cls):
        """Create an admin, a repairman and a portal user."""
        super().setUpClass()
        # Fixit Admin has full access through ir.model.access.csv
        cls.user = new_test_user(cls.env, login='fixit_admin', groups='fixit.group_fixit_admin')
        # Portal user is not in Fixit groups, so has no access
        cls.portal = new_test_user(cls.env, login='fixit_portal', groups='base.group_portal')
        # Fixit User sees only orders assigned to him (ir.rule)
        cls.repairman = new_test_user(cls.env, login='fixit_repairman', groups='fixit.group_fixit_user')

    # ---------- fixit.order ----------

    def test_order_access(self):
        """Admin can create orders, portal user cannot."""
        order = self.env['fixit.order'].with_user(self.user).create({'name': 'Phone'})
        self.assertEqual(order.create_uid, self.user)

        with self.assertRaises(AccessError) as error:
            self.env['fixit.order'].with_user(self.portal).create({'name': 'Phone'})
        self.assertIn('(fixit.order)', str(error.exception))

    # ---------- fixit.order: states ----------

    def test_order_states(self):
        """Buttons move the order step by step up to Picked Up."""
        order = self.env['fixit.order'].create({'name': 'Laptop'})
        self.assertEqual(order.state, 'new_request')
        order.action_diagnostics()
        order.action_approval()
        order.action_repair()
        order.action_ready()
        order.action_picked_up()
        self.assertEqual(order.state, 'picked_up')

    def test_order_cannot_skip_states(self):
        """A new order cannot jump straight to Picked Up."""
        order = self.env['fixit.order'].create({'name': 'Laptop'})
        with self.assertRaises(UserError) as error:
            order.action_picked_up()
        self.assertEqual(str(error.exception), 'This order cannot go to this status now.')
        self.assertEqual(order.state, 'new_request')

    def test_order_final_state(self):
        """A cancelled order cannot be moved anywhere."""
        order = self.env['fixit.order'].create({'name': 'Laptop'})
        order.action_cancel()
        with self.assertRaises(UserError) as error:
            order.action_diagnostics()
        self.assertEqual(str(error.exception), 'This order cannot go to this status now.')
        self.assertEqual(order.state, 'cancelled')

    # ---------- fixit.order.line ----------

    def test_order_line_subtotal(self):
        """Subtotal is quantity * price."""
        order = self.env['fixit.order'].create(
            {
                'name': 'Phone',
                'line_ids': [(0, 0, {'name': 'Battery', 'quantity': 2, 'price': 500})],
            }
        )
        self.assertEqual(order.line_ids.subtotal, 1000)

    def test_order_total(self):
        """Order total is the sum of line subtotals."""
        order = self.env['fixit.order'].create(
            {
                'name': 'Phone',
                'line_ids': [
                    (0, 0, {'name': 'Battery', 'quantity': 2, 'price': 500}),
                    (0, 0, {'name': 'Screen', 'quantity': 1, 'price': 1500}),
                ],
            }
        )
        self.assertEqual(order.amount_total, 2500)

    def test_order_line_quantity(self):
        """Quantity must be greater than zero."""
        order = self.env['fixit.order'].create({'name': 'Phone'})
        with self.assertRaises(IntegrityError) as error, mute_logger('odoo.sql_db'):
            self.env['fixit.order.line'].create({'name': 'Battery', 'quantity': 0, 'order_id': order.id})
        self.assertIn('check_quantity', str(error.exception))

    def test_order_line_access(self):
        """Portal user cannot read order lines."""
        order = (
            self.env['fixit.order']
            .with_user(self.user)
            .create(
                {
                    'name': 'Laptop',
                    'line_ids': [(0, 0, {'name': 'Change screen'})],
                }
            )
        )
        self.assertEqual(order.line_ids.order_id, order)

        with self.assertRaises(AccessError) as error:
            order.line_ids.with_user(self.portal).read(['name'])
        self.assertIn('(fixit.order.line)', str(error.exception))

    # ---------- fixit.part ----------

    def test_part_access(self):
        """Admin can create and edit parts, portal user cannot search them."""
        part = self.env['fixit.part'].with_user(self.user).create({'name': 'Battery', 'price': 500})
        part.write({'price': 450})
        self.assertEqual(part.price, 450)

        with self.assertRaises(AccessError) as error:
            self.env['fixit.part'].with_user(self.portal).search([])
        self.assertIn('(fixit.part)', str(error.exception))

    # ---------- fixit.device.type ----------

    def test_device_type_access(self):
        """Repairman can read device types but cannot create them."""
        laptop = self.env['fixit.device.type'].create({'name': 'Laptop'})
        self.assertEqual(laptop.with_user(self.repairman).warranty_months, 3)

        with self.assertRaises(AccessError) as error:
            self.env['fixit.device.type'].with_user(self.repairman).create({'name': 'Phone'})
        self.assertIn('(fixit.device.type)', str(error.exception))

    # ---------- fixit.device ----------

    def test_device_access(self):
        """Repairman can register a device but cannot delete it."""
        device = self.env['fixit.device'].with_user(self.repairman).create({'name': 'iPhone 15'})

        with self.assertRaises(AccessError) as error:
            device.unlink()
        self.assertIn('(fixit.device)', str(error.exception))
        self.assertTrue(device.exists())

    # ---------- ir.rule ----------

    def test_user_sees_less_orders_than_admin(self):
        """Record rules hide other repairmen orders and lines from a user."""
        self.env['fixit.order'].create(
            [
                {'name': 'Mine', 'repairman_id': self.repairman.id, 'line_ids': [(0, 0, {'name': 'Line 1'})]},
                {'name': 'Not mine', 'repairman_id': self.user.id, 'line_ids': [(0, 0, {'name': 'Line 2'})]},
            ]
        )
        Order = self.env['fixit.order']
        Line = self.env['fixit.order.line']

        user_orders = Order.with_user(self.repairman).search_count([])
        admin_orders = Order.with_user(self.user).search_count([])
        self.assertLess(user_orders, admin_orders)

        user_lines = Line.with_user(self.repairman).search_count([])
        admin_lines = Line.with_user(self.user).search_count([])
        self.assertLess(user_lines, admin_lines)

    # ---------- fixit.mass.reassign.repairman.wizard ----------

    def test_mass_reassign_repairman(self):
        """Wizard changes the repairman only on the selected orders."""
        orders = self.env['fixit.order'].create([{'name': 'Order 1'}, {'name': 'Order 2'}])
        other_order = self.env['fixit.order'].create({'name': 'Order 3'})

        # Orders selected in the list come to the wizard through active_ids
        wizard = (
            self.env['fixit.mass.reassign.repairman.wizard']
            .with_user(self.user)
            .with_context(
                active_ids=orders.ids,
            )
            .create({'repairman_id': self.repairman.id})
        )
        self.assertEqual(wizard.order_ids, orders)

        wizard.action_reassign()
        # Check each order: orders.repairman_id would pass even if only one was changed
        for order in orders:
            self.assertEqual(order.repairman_id, self.repairman)
        self.assertFalse(other_order.repairman_id)

    # ---------- fixit.order.report.wizard ----------

    def test_report_wizard_wrong_period(self):
        """Period start after period end raises an error."""
        wizard = self.env['fixit.order.report.wizard'].create(
            {
                'date_from': date(2026, 2, 1),
                'date_to': date(2026, 1, 1),
            }
        )
        with self.assertRaises(UserError) as error:
            wizard.action_show_report()
        self.assertEqual(str(error.exception), 'The period start cannot be later than the period end.')

    def test_report_wizard_no_orders(self):
        """Empty search result raises an error."""
        wizard = self.env['fixit.order.report.wizard'].create(
            {
                'date_from': date(2000, 1, 1),
                'date_to': date(2000, 1, 31),
            }
        )
        with self.assertRaises(UserError) as error:
            wizard.action_show_report()
        self.assertEqual(str(error.exception), 'No orders found for these filters.')

    def test_report_wizard_filters_by_repairman(self):
        """Report contains only orders of the selected repairman."""
        order = self.env['fixit.order'].create({'name': 'Mine', 'repairman_id': self.repairman.id})
        self.env['fixit.order'].create({'name': 'Not mine', 'repairman_id': self.user.id})

        # Repairmen selected in the users list become the wizard default
        wizard = (
            self.env['fixit.order.report.wizard']
            .with_context(
                active_model='res.users',
                active_ids=self.repairman.ids,
                discard_logo_check=True,
            )
            .create({})
        )
        self.assertEqual(wizard.repairman_ids, self.repairman)
        self.assertFalse(wizard.order_ids)

        action = wizard.action_show_report()
        self.assertEqual(action['context']['active_ids'], order.ids)
