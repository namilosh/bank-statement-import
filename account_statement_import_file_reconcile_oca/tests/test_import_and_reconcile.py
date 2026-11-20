# Copyright 2026 MJDPAK
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from unittest.mock import patch

from odoo.tests import common, tagged
from odoo.tools.binary import BinaryBytes


@tagged("post_install", "-at_install")
class TestImportAndReconcile(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.journal = cls.env["account.journal"].create(
            {"name": "Test bank journal", "code": "TBJ", "type": "bank"}
        )
        cls.wizard = (
            cls.env["account.statement.import"]
            .with_context(journal_id=cls.journal.id)
            .create(
                {
                    "statement_file": BinaryBytes(b"dummy"),
                    "statement_filename": "dummy.txt",
                }
            )
        )

    def _button(self, notifications):
        with patch.object(
            type(self.wizard),
            "_import_file",
            return_value={"statement_ids": [], "notifications": notifications},
        ):
            return self.wizard.import_file_and_reconcile_button()

    def test_button_returns_reconcile_action(self):
        action = self._button([])
        self.assertEqual(action["res_model"], "account.bank.statement.line")
        self.assertEqual(action["context"]["active_id"], self.journal.id)
        self.assertEqual(action["context"]["default_journal_id"], self.journal.id)
        self.assertTrue(action["context"]["search_default_not_reconciled"])

    def test_button_with_notifications(self):
        action = self._button(["Warning 1", "Warning 2"])
        self.assertEqual(action["tag"], "display_notification")
        self.assertEqual(action["params"]["message"], "Warning 1\n\nWarning 2")
        self.assertEqual(
            action["params"]["next"]["res_model"], "account.bank.statement.line"
        )
