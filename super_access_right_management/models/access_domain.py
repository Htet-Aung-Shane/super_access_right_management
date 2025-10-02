from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccessDomain(models.Model):
    _name = 'access.domain'
    _description = 'Access Domain'

    model_id = fields.Many2one('ir.model', string='Model', index=True, required=True,
                               ondelete='cascade', inverse="_inverse_model_id")
    model_name = fields.Char(string='Model Name', inverse="_inverse_model_name")
    domain = fields.Text(string='Domain', default='[]')

    access_right_mgmt_id = fields.Many2one('access.right.mgmt', 'Access Management')

    @api.onchange('model_name')
    def _inverse_model_name(self):
        for rec in self:
            model_id = self.env['ir.model'].search(
                [('model', '=', rec.model_name)]).id
            if model_id:
                rec.model_id = model_id

    @api.onchange('model_id')
    def _inverse_model_id(self):
        for rec in self:
            if rec.model_id:
                rec.model_name = rec.model_id.model
