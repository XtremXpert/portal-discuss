# Copyright 2026 Bemade Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests import HttpCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestPortalDm(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.portal_user = new_test_user(
            cls.env, login="pdd_portal", password="pdd_portal_pwd",
            groups="base.group_portal", name="Portal Alice",
        )
        cls.other_user = new_test_user(
            cls.env, login="pdd_other", password="pdd_other_pwd",
            groups="base.group_portal",
            name="Portal Bob",
        )

    def test_start_chat_and_list(self):
        self.authenticate("pdd_portal", "pdd_portal_pwd")
        response = self.url_open("/my/chats")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Aucune conversation", response.text)

        response = self.url_open(
            f"/portal-discuss/message/{self.other_user.id}", allow_redirects=False
        )
        self.assertEqual(response.status_code, 303)
        channel = self.env["discuss.channel"].search(
            [
                ("channel_type", "=", "chat"),
                ("channel_member_ids.partner_id", "=", self.portal_user.partner_id.id),
                ("channel_member_ids.partner_id", "=", self.other_user.partner_id.id),
            ]
        )
        self.assertEqual(len(channel), 1)
        self.assertTrue(
            response.headers["Location"].endswith(f"/discuss/channel/{channel.id}")
        )
        # The other portal user answers through the Discuss controller.
        self.authenticate("pdd_other", "pdd_other_pwd")
        self.make_jsonrpc_request(
            "/mail/message/post",
            {
                "thread_model": "discuss.channel",
                "thread_id": channel.id,
                "post_data": {"body": "Hello Alice", "message_type": "comment"},
            },
        )

        self.authenticate("pdd_portal", "pdd_portal_pwd")
        response = self.url_open("/my/chats")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Portal Bob", response.text)
        self.assertIn("Hello Alice", response.text)
        self.assertIn(f"/discuss/channel/{channel.id}", response.text)

        # The chat page itself opens for the portal member.
        response = self.url_open(f"/discuss/channel/{channel.id}")
        self.assertEqual(response.status_code, 200)

    def test_cannot_message_self(self):
        self.authenticate("pdd_portal", "pdd_portal_pwd")
        response = self.url_open(
            f"/portal-discuss/message/{self.portal_user.id}", allow_redirects=False
        )
        self.assertEqual(response.status_code, 303)
        self.assertTrue(response.headers["Location"].endswith("/my/chats"))
