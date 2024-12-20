/** @odoo-module **/
import { FormController } from '@web/views/form/form_controller';
import { patch } from "@web/core/utils/patch";
import { formView } from "@web/views/form/form_view";
import { useService } from "@web/core/utils/hooks";
import { onWillStart } from "@odoo/owl";

patch(FormController.prototype, {
//    setup() {
//        super.setup();
//        this.orm = useService("orm");
//        this.user = useService("user");
//        const { context } = this.env.searchModel;
//        this.activeModel = context.active_model;
//        this.activeId = context.active_id;
//        this.showOCR = this.orm.call(this.activeModel, "ocr_enabled", [])
//    }
    setup() {
        super.setup(...arguments);
        this.action = useService("action");
    },

    getStaticActionMenuItems() {
        const { activeActions } = this.archInfo;
        let val = super.getStaticActionMenuItems()
        val['ai_ocr'] =
        {
            sequence: 0,
            icon: "fa fa-file-text",
            description: "Digitize",
            callback: () => {
                const action = this.model.orm.call(this.props.resModel, "action_show_digitalize_wizard", [this.props.resId]);
                this.action.doAction(action);
//               return this.model.orm.call(this.props.resModel, "action_show_digitalize_wizard", [this.props.resId]);
            },
            skipSave: true,
        }
        return val
    },
});