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
        const is_putaway = this?.env?.model?.record?.picking_type_id?.is_put_away && this.line.qty_onhand_in_locations ? true : false
        // the below code is not necessary anymore
//        const bypass_reservation = this?.env?.model?.record?.picking_type_id?.bypass_reservation ? true : false
//        const jsonString = this.line.qty_onhand_in_locations.replace(/'/g, '"');
//        const locations = JSON.parse(jsonString);
//        const location_in_available_locations = locations.map(l=> l.id).includes(this.line.location_id.id)
//        return bypass_reservation && !location_in_available_locations
        return is_putaway
    },

    get availableLocations(){
        return this.line.qty_onhand_in_locations
    },

    LocationPath(location){
        const default_location =  this?.env?.model?.record?.picking_type_id?.is_put_away ? this.env.model._defaultDestLocation() : this.env.model._defaultLocation()
        return this._getLocationPath(default_location, location);
    },

});