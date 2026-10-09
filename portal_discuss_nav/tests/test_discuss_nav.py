# Copyright 2026 Bemade Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests import HttpCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestDiscussNav(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = new_test_user(
            cls.env, login="pdn_user", password="pdn_user_pwd",
            groups="base.group_user",
        )
        cls.channel = cls.env["discuss.channel"].create(
            {"name": "Nav channel", "channel_type": "channel", "group_public_id": False}
        )
        cls.channel._add_members(users=cls.user, post_joined_message=False)

    def test_nav_bar(self):
        url = f"/discuss/channel/{self.channel.id}"
        self.authenticate("pdn_user", "pdn_user_pwd")
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('class="o-pd-nav"', response.text)
        self.assertIn('href="/my"', response.text)
        self.assertIn("Retour", response.text)

        params = self.env["ir.config_parameter"].sudo()
        params.set_str("portal_discuss.nav_url", "/my/home")
        params.set_str("portal_discuss.nav_label", "Back home")
        response = self.url_open(url)
        self.assertIn('href="/my/home"', response.text)
        self.assertIn("Back home", response.text)

    def test_no_nav_bar_for_public(self):
        self.authenticate(None, None)
        response = self.url_open(f"/discuss/channel/{self.channel.id}")
        self.assertNotIn('class="o-pd-nav"', response.text)
