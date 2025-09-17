from odoo import api, fields, models, _

class AccessRightsMgmt(models.Model):
    _name = 'access.right.mgmt'
    _description = 'Access Rights Management'

    name = fields.Char('Name')
    is_readonly = fields.Boolean('Read Only The Whole System')
    active = fields.Boolean('Active', default=True)
    revoke_chatter = fields.Boolean('Revoke Chatter')
    user_ids = fields.Many2many('res.users', string="Access Users")
    revoke_developer_mode = fields.Boolean('Revoke Developer Mode')
