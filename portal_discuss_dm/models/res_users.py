# Copyright 2026 Bemade Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class ResUsers(models.Model):
    _inherit = "res.users"

    def _portal_discuss_can_message(self, other_user):
        """Extension point: may the current user start a direct message
        with ``other_user``? Default: yes for any non-internal-only
        pairing the caller already resolved. Override to plug blocking,
        allow-lists or membership checks (e.g. social_safety)."""
        self.ensure_one()
        return bool(other_user.exists() and other_user != self)
