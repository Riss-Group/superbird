from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection(selection_add=[('revised', 'Revised')])
    previous_revision_ids = fields.Many2many(
                comodel_name='purchase.order',
                relation='purchase_order_previous_revisions_rel',
                column1='current_po_id',
                column2='previous_po_id',
                string="Prev. Revisions"
            )
    previous_revision_count = fields.Integer(
                string="Prev. Revisions Count",
                compute="_compute_previous_revision_count"
            )
    source_id = fields.Many2one(
                comodel_name='purchase.order',
                string='Source PO'
            )
    revision_id = fields.Many2one(
                comodel_name='purchase.order',
                string='Revised PO'
            )
    vendor_related_buyer = fields.Many2one(related="partner_id.buyer_id", string="Vendor Buyer")


    @api.depends('previous_revision_ids')
    def _compute_previous_revision_count(self):
        """
        Compute the count of previous revisions for the purchase order.
        This includes all POs in the chain leading up to this one.
        """
        for record in self:
            previous_revisions = record.previous_revision_ids
            record.previous_revision_count = len(previous_revisions)

    def action_view_revisions(self):
        """
        Return a custom window action to display previous revisions of the purchase order.
        """
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': f"Revisions of {self.name}",
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain': [('id', 'in', self.previous_revision_ids.ids)],
            'target': 'current',
        }

    def button_revise(self):
        """
        Only appears after PO cancellation.
        Allows for user to basically duplicate the current PO and
        create a revised PO.

        Revised POs will have an added sequence to their name as 
        an indication

        We also indicate this revision in the chatter of the
        original PO.
        """
       
        for record in self:
            base_name = record.name
            if '-' in record.name:
                base_name, current_revision = record.name.rsplit('-', 1)
                if current_revision.isdigit():
                    revision_increment = int(current_revision) + 1
                else:
                    revision_increment = 1
            else:
                revision_increment = 1

            revision_name = f"{base_name}-{revision_increment:03d}"
            all_previous_revisions = record.previous_revision_ids.ids + [record.id]

            revised_po = record.copy({
                'name': revision_name,
                'source_id': record.id,
            })

            record.revision_id = revised_po.id
            revised_po.previous_revision_ids = [(6, 0, all_previous_revisions)] 

            record.message_post(
                body=f"New revision created: {revision_name}",
                subtype_xmlid='mail.mt_note'
            )
            record.state = 'revised'
        return {
            'type': 'ir.actions.act_window',
            'name': f"Revised PO - {revision_name}",
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': revised_po.id,  
            'target': 'current',  
            }
