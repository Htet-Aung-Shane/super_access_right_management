from odoo import fields, models, api, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    access_rights_mgmt_ids = fields.Many2many('access.right.mgmt','access_management_users_rel', 'user_id', 'access_rights_mgmt_id', 'Access Pack')
