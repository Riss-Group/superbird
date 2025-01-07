/** @odoo-module **/

import { ChatGPTPromptDialog } from '@web_editor/js/wysiwyg/widgets/chatgpt_prompt_dialog';
import { _t } from "@web/core/l10n/translation";
import { status } from "@odoo/owl";
import { AttachmentList } from "@mail/core/common/attachment_list";
import { Dialog } from "@web/core/dialog/dialog";


export class ChatGPTPromptDialog2 extends ChatGPTPromptDialog {
        static template = 'teos_ai_helper.AIPromptDialog';
        static components = { Dialog,AttachmentList };

        _generate(prompt, callback) {
        const protectedCallback = (...args) => {
            if (status(this) !== 'destroyed') {
                delete this.pendingRpcPromise;
                return callback(...args);
            }
        }
        this.pendingRpcPromise = this.rpc('/web_editor/generate_text_ai', {
            prompt,
            conversation_history: this.state.conversationHistory,
        }, { shadow: true });
        return this.pendingRpcPromise
            .then(content => protectedCallback(content))
            .catch(error => protectedCallback(_t(error.data?.message || error.message), true));
    }

    submitPrompt(ev) {
        this._freezeInput();
        ev.preventDefault();
        const prompt = this.state.prompt;
        this.state.messages.push({ author: 'user', text: prompt });
        const messageId = new Date().getTime();
        const conversation = { role: 'user', content: prompt };
        this.state.conversationHistory.push(conversation);
        this.state.messages.push({ author: 'assistant', id: messageId });
        this.state.prompt = '';
        this._generate(prompt, (content, isError) => {
            if (isError) {
                // There was an error, remove the prompt from the history.
                this.state.conversationHistory = this.state.conversationHistory.filter(c => c !== conversation);
            } else {
                // There was no error, add the response to the history.
                this.state.conversationHistory.push({ role: 'assistant', content });
            }
            const messageIndex = this.state.messages.findIndex(m => m.id === messageId);
            this.state.messages[messageIndex] = {
                author: 'assistant',
                text: content,
                //attachments: content[1],
                isError,
                id: messageId,
            };
            this._unfreezeInput();
        });
    }
}