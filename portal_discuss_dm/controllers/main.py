# Copyright 2026 Bemade Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# Pattern from diverse-cité (social_messaging_discuss): portal pages
# list, the native public Discuss page does the chat. sudo() bypasses
# the internal-only creation ACL WITHOUT changing env.user, so the
# right partner becomes a member of the chat.
from odoo import http
from odoo.http import request
from odoo.tools import html2plaintext


class PortalDiscussDm(http.Controller):

    @http.route(
        ["/my/chats"], type="http", auth="user", website=True, sitemap=False
    )
    def my_chats(self, **kwargs):
        user = request.env.user
        channels = request.env["discuss.channel"].sudo().search(
            [
                ("channel_type", "=", "chat"),
                ("channel_member_ids.partner_id", "=", user.partner_id.id),
            ],
            order="last_interest_dt desc",
        )
        chats = []
        for channel in channels:
            other = channel.channel_member_ids.partner_id.filtered(
                lambda p: p != user.partner_id
            )[:1]
            last = channel.message_ids.sorted("id", reverse=True)[:1]
            preview = (html2plaintext(last.body or "") or "").strip() if last else ""
            member = channel.channel_member_ids.filtered(
                lambda m: m.partner_id == user.partner_id
            )[:1]
            chats.append(
                {
                    "channel": channel,
                    "other": other,
                    "preview": preview[:80],
                    "unread": member.message_unread_counter if member else 0,
                }
            )
        return request.render(
            "portal_discuss_dm.chats_list", {"chats": chats, "page_name": "chats"}
        )

    @http.route(
        ["/portal-discuss/message/<int:user_id>"],
        type="http", auth="user", website=True,
    )
    def start_chat(self, user_id, **kwargs):
        other = request.env["res.users"].sudo().browse(user_id)
        if not request.env.user._portal_discuss_can_message(other):
            return request.redirect("/my/chats")
        channel = request.env["discuss.channel"].sudo()._get_or_create_chat(
            [other.partner_id.id]
        )
        return request.redirect("/discuss/channel/%s" % channel.id)
