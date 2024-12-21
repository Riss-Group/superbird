/** @odoo-module **/
import { FormController } from '@web/views/form/form_controller';
import { patch } from "@web/core/utils/patch";
import { formView } from "@web/views/form/form_view";
import { useService } from "@web/core/utils/hooks";
import { onWillStart } from "@odoo/owl";

patch(FormController.prototype, {
    setup() {
        super.setup(...arguments);
        this.action = useService("action");
    },

     getStaticActionMenuItems() {
        const { activeActions } = this.archInfo;
        let val = super.getStaticActionMenuItems()
        let ocr_enabled = this.model.orm.call(this.props.resModel, "show_ocr_button", [this.props.resId])
        let ai_enabled = this.model.orm.call(this.props.resModel, "show_ai_button", [this.props.resId])
        if (ai_enabled) {
            val['ai_query'] =
            {
                sequence: 0,
                icon: "fa fa-solid fa-magic",
                description: "Ask Me",
                callback: () => {
                    const action = this.model.orm.call(this.props.resModel, "action_show_ai_query_wizard", [this.props.resId]);
                    this.action.doAction(action);
                },
                skipSave: true,
            }
        }
        if (ocr_enabled){
            val['ai_ocr'] =
            {
                sequence: 1,
                icon: "fa fa-file-text",
                description: "Digitize",
                callback: () => {
                    const action = this.model.orm.call(this.props.resModel, "action_show_digitalize_wizard", [this.props.resId]);
                    this.action.doAction(action);
                },
                skipSave: true,
            }
        }
        return val
    },
});