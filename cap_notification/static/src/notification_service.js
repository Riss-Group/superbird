/** @odoo-module **/

import { notificationService } from "@web/core/notifications/notification_service";
import { patch } from "@web/core/utils/patch";
import { useService } from '@web/core/utils/hooks';
import { reactive } from "@odoo/owl";
import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { NotificationContainer } from "@web/core/notifications/notification_container";


patch(notificationService, {
    dependencies: ["rpc"],
    async start( env, { rpc } ) {
        let notifId = 0;
        const notifications = reactive({});
        let AUTOCLOSE_DELAY = 4000; // Default value
//        super.start(...arguments);

        try {
            const result = await rpc("/notification/get_autoclose_delay", {});
            AUTOCLOSE_DELAY = result || AUTOCLOSE_DELAY;
            console.log("Fetched AUTOCLOSE_DELAY:", AUTOCLOSE_DELAY);
        } catch (error) {
            console.error("Error fetching AUTOCLOSE_DELAY:", error);
        };

        this.AUTOCLOSE_DELAY = AUTOCLOSE_DELAY;
        registry.category("main_components").add(
            this.notificationContainer.name,
            {
                Component: this.notificationContainer,
                props: { notifications },
            },
            { sequence: 100 }
        );

        function add(message, options = {}) {
            const id = ++notifId;
            const closeFn = () => close(id);
            const props = Object.assign({}, options, { message, close: closeFn });
            const sticky = props.sticky;
            delete props.sticky;
            delete props.onClose;
            let closeTimeout;
            const refresh = sticky
                ? () => {}
                : () => {
                      closeTimeout = browser.setTimeout(closeFn, AUTOCLOSE_DELAY);
                  };
            const freeze = sticky
                ? () => {}
                : () => {
                      browser.clearTimeout(closeTimeout);
                  };
            props.refresh = refreshAll;
            props.freeze = freezeAll;
            const notification = {
                id,
                props,
                onClose: options.onClose,
                refresh,
                freeze,
            };
            notifications[id] = notification;
            if (!sticky) {
                closeTimeout = browser.setTimeout(closeFn, AUTOCLOSE_DELAY);
            }
            return closeFn;
        };

        function refreshAll() {
            for (const id in notifications) {
                notifications[id].refresh();
            }
        };

        function freezeAll() {
            for (const id in notifications) {
                notifications[id].freeze();
            }
        };

        function close(id) {
            if (notifications[id]) {
                const notification = notifications[id];
                if (notification.onClose) {
                    notification.onClose();
                }
                delete notifications[id];
            }
        };

        return { add };
    },
});
