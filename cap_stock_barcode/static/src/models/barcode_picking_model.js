/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import BarcodePickingModel from '@stock_barcode/models/barcode_picking_model';
import LineComponent from "@stock_barcode/components/line";
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";
import { BackorderDialog } from '@stock_barcode/components/backorder_dialog';
import {_t} from "@web/core/l10n/translation";


patch(BarcodePickingModel.prototype, {
    async setup() {
        super.setup();
    },
    lineIsFaulty(line) {
        return line.is_quarantine || line.barcode_qty_done > line.reserved_uom_qty;
    },
    getQtyDone(line) {
        let qtyDone = line.barcode_qty_done;
        return qtyDone;
    },
    getQtyDemand(line) {
        let qtyDemand = line.reserved_uom_qty || 0; // Start with reserved_uom_qty or default to 0
        if (line.not_done_qty) {
            qtyDemand -= line.not_done_qty;
        }

        if (line.is_quarantine) {
            qtyDemand = line.reserved_uom_qty;
        }

        return qtyDemand;
    },
    async save_barcode_qty_done(line) {
        await this.orm.write(this.lineModel, [line.id], { barcode_qty_done: line.barcode_qty_done });
    },

    updateLineQty(virtualId, qty = 1) {
        this.actionMutex.exec(() => {
            const line = this.pageLines.find(l => l.virtual_id === virtualId);
            line.barcode_qty_done += qty;
            this.save_barcode_qty_done(line);
            this.cache.dbIdCache['stock.move.line'][line.id]['barcode_qty_done'] = line.barcode_qty_done;
        });
    },

    get canBeValidate() {
        let result = super.canBeValidate;

        if (this.cache && this.cache.dbIdCache && this.cache.dbIdCache['stock.move.line']) {
            let movelines = this.cache.dbIdCache['stock.move.line'];

            if (typeof movelines === 'object' && movelines !== null) {
                const hasBarcodeQtyDoneGreaterThanZero = Object.values(movelines).some(
                    item => item.barcode_qty_done > 0
                );
                const allConditionsMet = Object.values(movelines).every(line =>
                    line.is_splited || line.barcode_qty_done === line.quantity
                );

                if (hasBarcodeQtyDoneGreaterThanZero) {
                    result = true;
                };
                if (!allConditionsMet && this.record.picking_type_code != 'incoming') {
                    result = allConditionsMet;
                };
            }
        }

    return result;
},

    lineCanBeEdited(line) {
        let res = super.lineCanBeEdited(line);
        if (!this.lastScanned.product || this.lastScanned.product.id != line.product_id.id){
            return false
        };
        return res;
    },

    getDisplayIncrementBtn(line) {
       let res = super.getDisplayIncrementBtn(line);
        if (!this.lastScanned.product || this.lastScanned.product.id != line.product_id.id){
            return false
        };
        return res;
    },

    async validate() {
        if (this.config.restrict_scan_dest_location == 'mandatory' &&
            !this.lastScanned.destLocation && this.selectedLine) {
            return this.notification(_t("Destination location must be scanned"), { type: "danger" });
        }
        if (this.config.lines_need_to_be_packed &&
            this.currentState.lines.some(line => this._lineNeedsToBePacked(line))) {
            return this.notification(_t("All products need to be packed"), { type: "danger" });
        }
        await this._setUser();
        if (this.config.create_backorder === 'ask') {
            // If there are some uncompleted lines, displays the backorder dialog.
            const uncompletedLines = [];
            const alreadyChecked = [];
            let atLeastOneLinePartiallyProcessed = false;
            for (let line of this.currentState.lines.filter(line => !line.is_quarantine)) {
                line = this._getParentLine(line) || line;
                if (alreadyChecked.includes(line.virtual_id)) {
                    continue;
                }
                // Keeps track of already checked lines to avoid to check multiple times grouped lines.
                alreadyChecked.push(line.virtual_id);
                let qtyDone = line.barcode_qty_done;
                if (qtyDone != line.reserved_uom_qty) {
                    // Checks if another move line shares the same move id and adds its quantity done in that case.
                    qtyDone += this.currentState.lines.reduce((additionalQtyDone, otherLine) => {
                        return otherLine.product_id.id === line.product_id.id
                            && otherLine.move_id === line.move_id
                            && !otherLine.reserved_uom_qty ?
                            additionalQtyDone + otherLine.barcode_qty_done : additionalQtyDone
                    }, 0);
                    if (qtyDone != line.reserved_uom_qty) { // Quantity done still insufficient.
                        uncompletedLines.push(line);
                    }
                }
                atLeastOneLinePartiallyProcessed = atLeastOneLinePartiallyProcessed || (qtyDone > 0);
            }
            if (this.showBackOrderDialog && atLeastOneLinePartiallyProcessed && uncompletedLines.length) {
                this.trigger("playSound");
                return this.dialogService.add(BackorderDialog, {
                    displayUoM: this.groups.group_uom,
                    uncompletedLines,
                    onApply: () => super.validate(),
                });
            }
        }
        if (this.record.return_id) {
            this.validateContext = {...this.validateContext, picking_ids_not_to_backorder: this.resId};
        }
        return await super.validate();
    },

    _lineIsNotComplete(line) {
        const currentLine = this._getParentLine(line) || line;
        const isNotComplete = currentLine.reserved_uom_qty && currentLine.barcode_qty_done < currentLine.reserved_uom_qty && !line.is_splited;
        if (!isNotComplete && currentLine.lines) { // Grouped lines/package lines have multiple sublines.
            for (const subline of currentLine.lines) {
                // For tracked product, a line with `qty_done` but no tracking number is considered as not complete.
                if (subline.product_id.tracking != 'none') {
                    if (subline.barcode_qty_done && !(subline.lot_id || subline.lot_name)) {
                        return true;
                    }
                } else if (subline.reserved_uom_qty && subline.barcode_qty_done < subline.reserved_uom_qty) {
                    return true;
                }
            }
        }
        return isNotComplete;
    }


})