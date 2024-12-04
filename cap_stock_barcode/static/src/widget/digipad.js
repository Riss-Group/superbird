/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Digipad } from '@stock_barcode/widgets/digipad';
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";
import {_t} from "@web/core/l10n/translation";



patch(Digipad.prototype, {
    _checkInputValue() {
        this.props.quantityField = "barcode_qty_done";
        super._checkInputValue();
        }
})