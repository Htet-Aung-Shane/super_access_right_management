from odoo import api, fields, models, _


class AccessRightsMgmt(models.Model):
    _name = 'access.right.mgmt'
    _description = 'Access Rights Management'

    name = fields.Char('Name')
    is_readonly = fields.Boolean('Read Only The Whole System')
    active = fields.Boolean('Active', default=True)
    revoke_chatter = fields.Boolean('Revoke Chatter')
    user_ids = fields.Many2many('res.users','access_management_users_rel','access_rights_mgmt_id', 'user_id', string="Access Users", domain=[
                                ('share', '=', False)])
    revoke_developer_mode = fields.Boolean('Revoke Developer Mode')

    # hide_menu
    revoke_menu_ids = fields.Many2many('ir.ui.menu', string="Revoke Menu")
    # hide_action
    revoke_action_ids = fields.One2many(
        'revoke.action','access_right_mgmt_id', string="Revoke Action")
    # hide_field
    revoke_field_ids = fields.One2many('revoke.field','access_right_mgmt_id', string="Revoke Field")    
    # hide_button_and_tab
    revoke_button_tab_ids = fields.One2many(
        'revoke.button.tab','access_right_mgmt_id', string="Revoke Button Tab")
    # access_domain
    domain_ids = fields.One2many('access.domain','access_right_mgmt_id', string="Access Domain")
