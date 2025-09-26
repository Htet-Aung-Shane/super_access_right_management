from odoo import fields, models, api, _
from lxml import etree


class RevokeButtonTab(models.Model):
    _name = 'revoke.button.tab'
    _description = 'Revoke Button Tab'

    access_right_mgmt_id = fields.Many2one('access.right.mgmt', 'Access Management')
    model_id = fields.Many2one('ir.model', string='Model', index=True, required=True, ondelete='cascade',compute="_compute_model_id",store=True,readonly=False)
    model_name = fields.Char(string='Model Name', related='model_id.model', readonly=False, store=True)

    btn_model_nodes_ids = fields.Many2many(
        'store.model.nodes',
        string='Revoke Button',
        domain="[('node_option','=','button')]",
        relation='revoke_button_tab_store_model_nodes_btn_rel',
        column1='revoke_button_tab_id',
        column2='store_node_btn_id'
    )
    
    page_model_nodes_ids = fields.Many2many(
        'store.model.nodes',
        string='Revoke Tab/Page',
        domain="[('node_option','=','page')]",
        relation='revoke_button_tab_store_model_nodes_page_rel',
        column1='revoke_button_tab_id',
        column2='store_node_page_id'
    )

    @api.depends('model_name')
    def _compute_model_id(self):
        for rec in self:
            model_id = self.env['ir.model'].search([('model','=',rec.model_name)]).id
            if model_id:
                rec.model_id = model_id