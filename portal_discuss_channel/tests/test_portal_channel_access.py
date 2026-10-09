# Copyright 2026 Bemade Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestPortalChannelAccess(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.portal_user = new_test_user(
            cls.env, login="pdc_portal", groups="base.group_portal"
        )
        cls.other_portal = new_test_user(
            cls.env, login="pdc_portal_2", groups="base.group_portal"
        )
        Channel = cls.env["discuss.channel"]
        cls.member_channel = Channel.create(
            {"name": "Portal members", "channel_type": "channel"}
        )
        cls.member_channel._add_members(
            users=cls.portal_user | cls.other_portal, post_joined_message=False
        )
        cls.other_channel = Channel.create(
            {"name": "Internal only", "channel_type": "channel"}
        )
        Member = cls.env["discuss.channel.member"]
        cls.own_line = Member.search(
            [
                ("channel_id", "=", cls.member_channel.id),
                ("partner_id", "=", cls.portal_user.partner_id.id),
            ]
        )
        cls.other_line = Member.search(
            [
                ("channel_id", "=", cls.member_channel.id),
                ("partner_id", "=", cls.other_portal.partner_id.id),
            ]
        )

    def test_channel_access(self):
        """Portal users see the group channels they belong to, and only them."""
        # Core rules restrict "channel" channels to internal users.
        self.assertEqual(
            self.member_channel.group_public_id, self.env.ref("base.group_user")
        )
        channels = (
            self.env["discuss.channel"]
            .with_user(self.portal_user)
            .search([("channel_type", "=", "channel")])
        )
        self.assertIn(self.member_channel, channels)
        self.assertNotIn(self.other_channel, channels)
        self.member_channel.with_user(self.portal_user).check_access("read")
        with self.assertRaises(AccessError):
            self.other_channel.with_user(self.portal_user).check_access("read")
        with self.assertRaises(AccessError):
            self.member_channel.with_user(self.portal_user).check_access("write")

    def test_member_access(self):
        """Portal members read co-members and manage only their own line."""
        members = (
            self.env["discuss.channel.member"]
            .with_user(self.portal_user)
            .search([("channel_id", "=", self.member_channel.id)])
        )
        self.assertIn(self.own_line, members)
        self.assertIn(self.other_line, members)
        self.own_line.with_user(self.portal_user).check_access("write")
        self.own_line.with_user(self.portal_user).check_access("unlink")
        with self.assertRaises(AccessError):
            self.other_line.with_user(self.portal_user).check_access("write")
        with self.assertRaises(AccessError):
            self.other_line.with_user(self.portal_user).check_access("unlink")
