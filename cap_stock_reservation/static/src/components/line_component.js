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