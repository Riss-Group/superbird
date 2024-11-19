/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";
import { BackorderDialog } from '@stock_barcode/components/backorder_dialog';
import {_t} from "@web/core/l10n/translation";


patch(BackorderDialog.prototype, {
    async setup() {
        super.setup();
        this.orm = useService("orm");
        this.scrap_quantities = useState({});
        this.loadScrapQuantities();
    },
    async loadScrapQuantities() {
    for (const line of this.props.uncompletedLines) {
        const qty = await this.get_scrap_qty(line);
        this.scrap_quantities[line.id] = qty; // Reactive update
    }
},

    async get_scrap_qty(line){
     const not_done_qty_id = await this.orm.searchRead(
            "stock.move.line",
            [
                ["product_id", "=", line.product_id.id],
                ["move_id", "=", line.move_id],
                ["id", "=", line.id],
            ],
            ["not_done_qty"]
        );
        return not_done_qty_id.length ? not_done_qty_id[0].not_done_qty : 0;
        }
    })