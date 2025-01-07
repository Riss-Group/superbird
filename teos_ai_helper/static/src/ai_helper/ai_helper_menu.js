/** @odoo-module **/

import { Wysiwyg } from "@web_editor/js/wysiwyg/wysiwyg";
import * as OdooEditorLib from "@web_editor/js/editor/odoo-editor/src/OdooEditor";
import { registry } from "@web/core/registry";
import { Component, useChildSubEnv, useState } from "@odoo/owl";
import { debounce } from "@web/core/utils/timing";
import { useService } from "@web/core/utils/hooks";
import { ChatGPTPromptDialog2 } from '@teos_ai_helper/ai_helper/chatgpt_prompt_dialog';
import { _t } from "@web/core/l10n/translation";
const { onWillStart, useComponent } = owl;



export class AIHelperMenu extends Component {
    static template = "teos_ai_helper.AIHelperMenu";
    static props = {};
    static toggleDelay = 1000;


    setup() {
        this.companyService = useService("company");

    }

    openChatGPTDialog(mode = 'prompt') {
        const odooEditor = OdooEditorLib.OdooEditor;
        //const preserveCursor = OdooEditorLib.preserveCursor;
        //odooEditor.document = document.createElement('div');
        //const restore = preserveCursor(document.createElement('div'));
        const params = {
            insert: content => {
                odooEditor.historyPauseSteps();
                const insertedNodes = odooEditor.execCommand('insert', content);
                odooEditor.historyUnpauseSteps();
                this.notification.add(_t('Your content was successfully generated.'), {
                    title: _t('Content generated'),
                    type: 'success',
                });
                odooEditor.historyStep();
                // Add a frame around the inserted content to highlight it for 2
                // seconds.
                const start = insertedNodes?.length && closestElement(insertedNodes[0]);
                const end = insertedNodes?.length && closestElement(insertedNodes[insertedNodes.length - 1]);
                if (start && end) {
                    const divContainer = odooEditor.editable.parentElement;
                    let [parent, left, top] = [start.offsetParent, start.offsetLeft, start.offsetTop - start.scrollTop];
                    while (parent && !parent.contains(divContainer)) {
                        left += parent.offsetLeft;
                        top += parent.offsetTop - parent.scrollTop;
                        parent = parent.offsetParent;
                    }
                    let [endParent, endTop] = [end.offsetParent, end.offsetTop - end.scrollTop];
                    while (endParent && !endParent.contains(divContainer)) {
                        endTop += endParent.offsetTop - endParent.scrollTop;
                        endParent = endParent.offsetParent;
                    }
                    const div = document.createElement('div');
                    div.classList.add('o-chatgpt-content');
                    const FRAME_PADDING = 3;
                    div.style.left = `${left - FRAME_PADDING}px`;
                    div.style.top = `${top - FRAME_PADDING}px`;
                    div.style.width = `${Math.max(start.offsetWidth, end.offsetWidth) + (FRAME_PADDING * 2)}px`;
                    div.style.height = `${endTop + end.offsetHeight - top + (FRAME_PADDING * 2)}px`;
                    divContainer.prepend(div);
                    setTimeout(() => div.remove(), 2000);
                }
            },
        };
        //if (mode === 'alternatives') {
        //    params.originalText = odooEditor.document.getSelection().toString() || '';
        //}
        //odooEditor.document.getSelection().collapseToEnd();
        this.env.services.dialog.add(
            ChatGPTPromptDialog2,
            params,
           //{ onClose: restore },
        );
    }

    OpenAIpopup() {
                    this.openChatGPTDialog();
}}

export const systrayItem = {
    Component: AIHelperMenu,
    isDisplayed(env) {
    console.log(env);
    return env.services.user.isAiUser;
    },
};

registry.category("systray").add("AIHelperMenu", systrayItem, { sequence: 99 });
