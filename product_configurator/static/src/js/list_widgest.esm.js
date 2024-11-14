/* @odoo-module */
import {ListController} from "@web/views/list/list_controller";
import {onMounted} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";

patch(ListController.prototype, {
    setup() {
        super.setup(...arguments);
        onMounted(() => {
            var form_element = this.rootRef.el;
            var self = this;
            if (
                self.model.config.resModel === "product.product" &&
                self.model.config.context.custom_create_variant
            ) {
                var buttons = form_element.querySelector(
                    ".o_control_panel_main_buttons"
                );
                var createButtons = buttons.querySelectorAll(".o_list_button_add");
                createButtons.forEach((button) => {
                    button.style.display = "none";
                });
            }
        });
    },
});
