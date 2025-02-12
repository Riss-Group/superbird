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

    canBeSplit(line) {
        const split = this.line.barcode_qty_done > 0 &&
                        this.line.barcode_qty_done < this.line.quantity &&
                        !line.is_splited && this.env.model.record.picking_type_id.split_lines ? true : false;
        return split
    },

    get isComplete() {
        const result = super.isComplete;
        const isComplete = this.line.is_quarantine || this.line.barcode_qty_done > this.line.reserved_uom_qty ? false : result;
        return isComplete
            },

    async SplitRemainingQty(line) {
        const fieldsParams = {
            location_id: line.location_id.id,
            location_dest_id: this.env.model.record.location_dest_id,
        };

        const newLine = await this.env.model._createNewLine({ copyOf: line, fieldsParams });

        const remainingQty = line.quantity - line.barcode_qty_done;
        Object.assign(newLine, {
            qty_done: remainingQty,
            quantity: remainingQty,
            reserved_uom_qty: remainingQty,
            barcode_qty_done: 0,
            lot_id: false, // Ensure no lot is associated
            lot_name: false,
        });

        Object.assign(line, {
            qty_done: line.barcode_qty_done,
            quantity: line.barcode_qty_done,
            reserved_uom_qty: line.barcode_qty_done,
        });
        const data = { quantity: line.barcode_qty_done };
        await this.env.model.save();
        await this.env.model.save_barcode_data(line, data);

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

    get displayAvailableLocation(){
        const bypass_reservation = this?.env?.model?.record?.picking_type_id?.bypass_reservation ? true : false
        const jsonString = this.line.qty_onhand_in_locations.replace(/'/g, '"');
        const locations = JSON.parse(jsonString);
        const location_in_available_locations = locations.map(l=> l.id).includes(this.line.location_id.id)
        return bypass_reservation && !location_in_available_locations
    },

    get availableLocations(){
        const jsonString = this.line.qty_onhand_in_locations.replace(/'/g, '"');
        const locations = JSON.parse(jsonString);
        return locations
    },

    LocationPath(location){
        return this._getLocationPath(this.env.model._defaultLocation(), location);
    },

});