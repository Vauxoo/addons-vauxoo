odoo.define("account_bank_reconcile_transfer.bank_reconciliation", function (require) {
    "use strict";

    const LineRenderer = require("account.ReconciliationRenderer").LineRenderer;
    const StatementModel = require("account.ReconciliationModel").StatementModel;
    const relationalFields = require("web.relational_fields");

    StatementModel.include({
        init: function () {
            this._super.apply(this, arguments);
            this.quickCreateFields = [...this.quickCreateFields, "transfer_journal_id"];
        },

        updateProposition: function (handle, values) {
            if ("transfer_journal_id" in values && values.transfer_journal_id) {
                const self = this;
                const superCall = self._super;
                return new Promise(function (resolve) {
                    self._rpc({
                        model: "res.company",
                        method: "read",
                        args: [self.getLine(handle).st_line.company_id, ["transfer_account_id"]],
                    }).then(function (result) {
                        const account = result[0]["transfer_account_id"];
                        values.account_id = {
                            id: account[0],
                            display_name: account[1],
                        };
                        superCall.apply(self, [handle, values]).then(function () {
                            resolve();
                        });
                    });
                });
            }
            return this._super(handle, values);
        },

        _formatToProcessReconciliation: function (line, prop) {
            const result = this._super(line, prop);

            if (prop.transfer_journal_id) result.transfer_journal_id = prop.transfer_journal_id.id;

            return result;
        },
    });

    LineRenderer.include({
        _renderCreate: function (state) {
            const self = this;
            return self._super(state).then(function () {
                const record = self.model.get(self.handleCreateRecord);

                record.fields.transfer_journal_id = {
                    relation: "account.journal",
                    type: "many2one",
                    domain: [
                        ["company_id", "=", state.st_line.company_id],
                        ["id", "!=", state.st_line.journal_id],
                        ["type", "in", ["bank", "cash"]],
                    ],
                };

                self.fields.transfer_journal_id = new relationalFields.FieldMany2One(
                    self,
                    "transfer_journal_id",
                    record,
                    {mode: "edit"}
                );
                self.fields.transfer_journal_id.appendTo(self.$(".create .transfer_journal_id .o_td_field"));
            });
        },
    });
});
