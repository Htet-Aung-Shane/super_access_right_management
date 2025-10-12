from odoo import fields, models, api, _


class RevokeAction(models.Model):
    _name = 'revoke.action'
    _description = "Revoke Action Access Rights"

    access_right_mgmt_id = fields.Many2one(
        'access.right.mgmt', 'Access Management')
    model_id = fields.Many2one(
        'ir.model', 'Model', compute="_compute_model_id", store=True, readonly=False)
    model_name = fields.Char(
        string='Model Name', related='model_id.model', readonly=False, store=True)
    server_action_ids = fields.Many2many('action.data', 'revoke_action_server_action_data_rel_ah', 'revoke_action_id',
                                         'server_action_id', 'Revoke Actions',
                                         domain="[('action_id.binding_model_id','=',model_id),('action_id.type','!=','ir.actions.report')]")
    report_action_ids = fields.Many2many('action.data', 'revoke_action_report_action_data_rel_ah', 'revoke_action_id',
                                         'report_action_id', 'Revoke Reports',
                                         domain="[('action_id.binding_model_id','=',model_id),('action_id.type','=','ir.actions.report')]")
    revoke_export = fields.Boolean('Revoke Export')
    is_readonly = fields.Boolean('Read-Only')

    revoke_create = fields.Boolean('Revoke Create')
    revoke_edit = fields.Boolean('Revoke Edit')
    revoke_delete = fields.Boolean('Revoke Delete')

    revoke_archive_unarchive = fields.Boolean('Revoke Archive/Unarchive')
    revoke_duplicate = fields.Boolean('Revoke Duplicate')
    revoke_chatter = fields.Boolean('Revoke Chatter')

    @api.depends('model_name')
    def _compute_model_id(self):
        for rec in self:
            model_id = self.env['ir.model'].search(
                [('model', '=', rec.model_name)]).id
            if model_id:
                rec.model_id = model_id
