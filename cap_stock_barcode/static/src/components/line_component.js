/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import LineComponent from "@stock_barcode/components/line";
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";
import { ManualBarcodeScanner } from "@stock_barcode/components/manual_barcode";
import {_t} from "@web/core/l10n/translation";



patch(LineComponent.prototype, {
    setup() {
        super.setup();
        this.action = useService("action");
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.dialog = useService('dialog');
    },
    get isComplete() {
        const result = super.isComplete;
        const isComplete = this.line.is_quarantine || this.line.barcode_qty_done > this.line.reserved_uom_qty ? false : result;
        return isComplete
            },
    async SplitRemainingQty(line) {
        await this.env.model.save();
        const res = await this.orm.call(
            'stock.move.line',
            'split_line_with_qty_remaining',
            [[line.id]]
        );
        return this.env.model.trigger('refresh');
    },
    async printProductBarcode(line) {
        const action = await this.action.loadAction(
            "product.action_open_label_layout"
        );
        action.context = {'default_product_ids' : [line.product_id.id], 'default_print_format' : '4x12', 'default_hide_price_fields' : true}
        this.action.doAction({...action, default_product_ids: line.product_id.id});
//        const reportFile = 'stock.label_product_product_view';
//        return this.action.doAction({
//            type: "ir.actions.report",
//            report_type: "qweb-pdf",
//            report_name: `${reportFile}?docids=${line.product_id.id}&quantity=${1}`,
//            report_file: reportFile,
//        });
    },
    async updateProductBarcode(line) {
    self = this;
        this.dialog.add(ManualBarcodeScanner, {
            openMobileScanner: async () => {
                await this.openMobileScanner();
            },
            onApply: async (barcode) => {
                barcode = this.env.model.cleanBarcode(barcode);
                const res = await this.orm.call(
                    'stock.move.line',
                    'update_product_barcode',
                    [[line.id],barcode]
                );
                 if (res) {
                    const dbBarcodeCache = self.env.model.cache.dbBarcodeCache;

                    if (!dbBarcodeCache['product.product']) {
                        dbBarcodeCache['product.product'] = {};
                    }

                    if (!dbBarcodeCache['product.product'][barcode]) {
                        dbBarcodeCache['product.product'][barcode] = [];
                    }
                    dbBarcodeCache['product.product'][barcode].push(line.product_id.id);

                } else {
                    console.error("Failed to update barcode in dbBarcodeCache.");
                            }
            return barcode;
            }
        });
    },
});