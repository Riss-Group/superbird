/** @odoo-module **/

import { onWillStart, Component, useState, useRef, onMounted, onWillUpdateProps} from '@odoo/owl';
import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";
import { Field, getFieldFromRegistry } from "@web/views/fields/field";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";
import { Record } from "@web/model/record";

export class AIChatter extends Component {
    setup() {
        super.setup();
        this.orm = useService('orm');
        this.rpc = useService('rpc');
        this.action = useService("action");
        this.state = useState({
            messages: [],
            newMessage: '',
        });

        this.inputRef = useRef('messageInput');
        onWillStart(async () => {
            await this.fetchMessages(this.props.record);
        });
        onWillUpdateProps(async (nextProps) => {
            await this.fetchHierarchy(nextProps.record);
        });
    }

    async fetchMessages(record) {
        // Fetch aIChatter messages using RPC
        this.state.messages = await this.rpc('/ai_chatter/messages', {
            model: record.resModel,
            id: record.resId,
        });
    }

    async sendMessage() {
        if (this.state.newMessage.trim() === '') {
            return;
        }

        await this.rpc('/ai_chatter/post_message', {
            model: this.props.record.resModel,
            id: this.props.record.resId,
            message: this.state.newMessage,
        });

        this.state.newMessage = '';
        this.fetchMessages(this.props.record);
    }
}
AIChatter.template = 'AIChatterTemplate';
AIChatter.props = {
    ...standardWidgetProps,
};

export const aIChatter = {
    component: AIChatter,
    fieldDependencies: [{ name: "message_ids", type: "one2many" }],
};
registry.category("view_widgets").add("ai_chatter", aIChatter);