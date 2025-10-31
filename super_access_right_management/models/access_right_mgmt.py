from odoo import api, fields, models, _


class AccessRightsMgmt(models.Model):
    _name = 'access.right.mgmt'
    _description = 'Access Rights Management'

    name = fields.Char('Name')
    is_readonly = fields.Boolean('Read Only The Whole System')
    active = fields.Boolean('Active', default=True)
    revoke_chatter = fields.Boolean('Revoke Chatter')
    user_ids = fields.Many2many('res.users','access_management_users_rel','access_right_mgmt_id', 'user_id', string="Access Users", domain=[
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

    @api.model
    def is_archive_unarchive(self, model):
        revoke_actions = self.env['revoke.action'].sudo().search([
            ('access_right_mgmt_id', 'in', self.env.user.access_rights_mgmt_ids.ids),
            ('model_id.model', '=', model)])
        result = False
        if revoke_actions:
            for revoke_action in revoke_actions:
                if revoke_action.revoke_archive_unarchive:
                    result = True

        return result
    
    @api.model
    def is_export(self, model):
        revoke_actions = self.env['revoke.action'].sudo().search([
            ('access_right_mgmt_id', 'in', self.env.user.access_rights_mgmt_ids.ids),
            ('model_id.model', '=', model)])
        result = False
        if revoke_actions:
            for revoke_action in revoke_actions:
                if revoke_action.revoke_export:
                    result = True

        return result
    
    def write(self, vals):
        res = super(AccessRightsMgmt, self).write(vals)
        self.env.registry.clear_cache()
        return res

    def unlink(self):
        res = super(AccessRightsMgmt, self).unlink()
        self.env.registry.clear_cache()
        return res