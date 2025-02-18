/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import MainComponent from '@stock_barcode/components/main';
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { onWillStart } from "@odoo/owl";


patch(MainComponent.prototype, {
    setup() {
        this.orm = useService("orm");
        onWillStart(async () => {
            await this.rpc('/stock_barcode/reassign_moves', {
                model: this.resModel,
                res_id: this.resId,
            });
        });
        super.setup();

    },
});


