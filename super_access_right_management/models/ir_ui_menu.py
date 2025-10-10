from odoo import api, fields, models


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def search(self, args, offset=0, limit=None, order=None,):
        ids = super(IrUiMenu, self).search(args, offset=0, limit=None, order=order)
        user = self.env.user
        hide_menu_ids = user.access_rights_mgmt_ids.mapped('revoke_menu_ids')
        ids = ids - hide_menu_ids
        return ids
