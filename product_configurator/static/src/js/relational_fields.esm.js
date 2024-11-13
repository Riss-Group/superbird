/** @odoo-module **/
import {Many2OneField} from "@web/views/fields/many2one/many2one_field";
import {patch} from "@web/core/utils/patch";

patch(Many2OneField.prototype, {
    // eslint-disable-next-line no-unused-vars
    computeActiveActions(props) {
        var element = super.computeActiveActions(...arguments);
        if (element === undefined) {
            return $();
        }
        return element;
    },
});
