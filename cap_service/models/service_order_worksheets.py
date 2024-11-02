from odoo import models, fields, api, _


class ServiceOrderWorksheets(models.Model):
    _name = 'service.order.worksheets'
    _description = "Service Order Worksheets"
    _rec_name = 'task_id'
    _auto = False
    

    service_order_id = fields.Many2one('service.order', string="Service Order", readonly=True)
    worksheet_id = fields.Integer(string="Worksheet ID", readonly=True)
    model_name = fields.Char(string="Model Name", readonly=True)
    worksheet_name = fields.Char(string="Worksheet Name", readonly=True)
    task_id = fields.Many2one('project.task', readonly=True)
    external_id_to_create = fields.Char(string='External ID to Create', store=False, copy=False)


    @property
    def _table_query(self):
        service_order_ctx = self.env.context.get('service_order_ids')
        if not service_order_ctx:
            return self.return_nulls()
        service_order_ids = self.env['service.order'].browse(service_order_ctx)
        queries = []
        for service_order in service_order_ids:
            worksheet_references = service_order.worksheet_references or []
            unique_references = {(ref['model'], ref['id'], ref['task_id']) for ref in worksheet_references}
            for model_name, worksheet_id, task_id in unique_references:
                if model_name and worksheet_id and task_id:
                    queries.append(f"""
                        SELECT 
                        {task_id} AS id, 
                        {service_order.id} AS service_order_id,
                        {worksheet_id} AS worksheet_id,
                        '{model_name}' AS model_name,
                        {task_id} AS task_id,
                        x_name AS worksheet_name
                        FROM {model_name}
                        WHERE id = {worksheet_id}
                    """)
        combined_query = " UNION ALL ".join(queries) if queries else self.return_nulls()
        return combined_query
            
    @api.model
    def return_nulls(self):
        return """
            SELECT 
            0 AS id,
            NULL AS service_order_id,
            NULL AS worksheet_id,
            NULL AS model_name,
            NULL AS task_id,
            NULL AS worksheet_name
        """
    
    def task_action_fsm_worksheet(self):
        action = self.task_id.action_fsm_worksheet()
        return action

