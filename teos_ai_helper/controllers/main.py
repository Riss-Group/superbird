import logging
from odoo.http import request
from odoo import http, _
from odoo.exceptions import UserError, AccessError
from odoo.addons.iap.tools import iap_tools
from odoo import release
from odoo.addons.web_editor.controllers.main import Web_Editor
import pandas as pd
logger = logging.getLogger(__name__)
DEFAULT_OLG_ENDPOINT = 'https://olg.api.odoo.com'
from odoo.http import request


class MyCustomWebEditorController(Web_Editor):

    def get_table_names(self):
        """
        Gets the table names that should be included in the search from the company settings.
        :return:
        """
        # request.env.cr.execute("""
        #                            SELECT table_name
        #                            FROM information_schema.tables
        #                            WHERE table_schema='public'
        #                            AND table_type='BASE TABLE';
        #                          """)
        #return request.env.cr.fetchall()
        model_list = request.env.company.ai_model_ids.mapped('model')
        table_list = [x.replace('.','_') for x in model_list]
        return table_list

    def get_random_rows(self, name_table, n=5):
        """
        For each model select 4 random rows
        :param name_table:
        :param n:
        :return:
        """
        query = "SELECT * FROM {} ORDER BY RANDOM() LIMIT 4;".format(name_table)
        return pd.read_sql(query, request.env.registry)

    def get_table_definitions(self):
        """
        For each table return a table definition consisting of random rows from the table
        :return:
        """
        markdown = []
        markdown.append("### table definition")
        table_list = self.get_table_names()
        if not table_list:
            raise Warning('Please make sure the AI models in settings are filled !!')
        for table in table_list:
            markdown.append(f'### {table}')
            markdown.append(f'###### Sample from data in json format')
            dt = self.get_random_rows(table)
            json_data = dt.to_json(orient='records')
            markdown.append(json_data)
            markdown.append(f'### End definition {table}')
            markdown.append('\n')
        table_definitions = '\n'.join(markdown)
        table_definitions = table_definitions + '\n---\nReturn the SQL Query for:'
        return table_definitions

    def parse_result_in_natural_language(self, result, conversation_history):
        """
        Turns the search result from the query into a human natural language
        :param result:
        :param conversation_history:
        :return:
        """
        IrConfigParameter = request.env['ir.config_parameter'].sudo()
        olg_api_endpoint = IrConfigParameter.get_param('web_editor.olg_api_endpoint', DEFAULT_OLG_ENDPOINT)
        response = iap_tools.iap_jsonrpc(olg_api_endpoint + "/api/olg/1/chat", params={
            'prompt': "You translate the result of a query into a natural language" + "\n" + result,
            'conversation_history': conversation_history or [],
            'version': release.version,
        }, timeout=30)
        if response['status'] == 'success':
            return response['content']


    @http.route("/web_editor/generate_text_ai", type="json", auth="user")
    def generate_text_ai(self, prompt, conversation_history):
        """
        Send the prompt into the odoo AI server, And convert the query result into human like language.
        :param prompt:
        :param conversation_history:
        :return:
        """
        table_definitions = self.get_table_definitions()
        prompt_context = request.env.company.ai_prompt
        if not prompt:
            prompt_context = """You are a Postgres expert and Odoo expert
                     Given the table names, Definitions and a prompt.
                     You only return sql queries that we can run directly no natural language,
                     Strictly stick to columns and table names provided in the table definition
                     The question is:
                    """
        prompt_2 = table_definitions + prompt_context + prompt
        try:
            IrConfigParameter = request.env['ir.config_parameter'].sudo()
            olg_api_endpoint = IrConfigParameter.get_param('web_editor.olg_api_endpoint', DEFAULT_OLG_ENDPOINT)
            response = iap_tools.iap_jsonrpc(olg_api_endpoint + "/api/olg/1/chat", params={
                'prompt': prompt_2,
                'conversation_history': conversation_history or [],
                'version': release.version,
            }, timeout=30)
            if response['status'] == 'success':
                sql_query = response['content'].replace('sql', '')
                sql_query = sql_query.replace("```", '')
                result = pd.read_sql(sql_query, request.env.registry).to_markdown()
                result = self.parse_result_in_natural_language(result, conversation_history)
                return result
            elif response['status'] == 'error_prompt_too_long':
                raise UserError(_("Sorry, your prompt is too long. Try to say it in fewer words."))
            else:
                raise UserError(_("Sorry, we could not generate a response. Please try again later."))
        except AccessError:
            raise AccessError(_("Oops, it looks like our AI is unreachable!"))
