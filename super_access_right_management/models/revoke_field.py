from odoo import api, fields, models


class RevokeField(models.Model):
    _name = 'revoke.field'
    _description = 'Revoke Field'

    access_right_mgmt_id = fields.Many2one(
        'access.right.mgmt', 'Access Management')
    model_id = fields.Many2one(
        'ir.model', 'Model', compute="_compute_model_id", store=True, readonly=False)
    model_name = fields.Char(string='Model Name', related='model_id.model',
                             readonly=False, store=True, inverse='_inverse_model_name')

    field_ids = fields.Many2many('ir.model.fields', string='Revoke Fields')

    is_invisible = fields.Boolean('IsInvisible')
    is_readonly = fields.Boolean('Is ReadOnly')
    is_required = fields.Boolean('Is Required')
    is_revoke_external_link = fields.Boolean('Revoke External Link')

    @api.depends('model_name')
    def _compute_model_id(self):
        for rec in self:
            model_id = self.env['ir.model'].search(
                [('model', '=', rec.model_name)]).id
            if model_id:
                rec.model_id = model_id
