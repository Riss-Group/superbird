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
        onWillStart(async () => {
            this.ocr_enabled = await this.model.orm.call(this.props.resModel, "show_ocr_button", [this.props.resId]);
            this.ai_enabled = await this.model.orm.call(this.props.resModel, "show_ai_button", [this.props.resId]);
        });
    },

     getStaticActionMenuItems() {
        const { activeActions } = this.archInfo;
        let val = super.getStaticActionMenuItems()
        val['ai_query'] =
        {
            isAvailable: () => this.ai_enabled,
            sequence: 0,
            icon: "fa fa-solid fa-magic",
            description: "Ask Me",
            callback: () => {
                const action = this.model.orm.call(this.props.resModel, "action_show_ai_query_wizard", [this.props.resId]);
                this.action.doAction(action);
            },
            skipSave: true,
        }

        val['ai_ocr'] =
        {
            isAvailable: () => this.ocr_enabled,
            sequence: 1,
            icon: "fa fa-file-text",
            description: "Digitize",
            callback: () => {
                const action = this.model.orm.call(this.props.resModel, "action_show_digitalize_wizard", [this.props.resId]);
                this.action.doAction(action);
            },
            skipSave: true,
        }
        return val
    },
});