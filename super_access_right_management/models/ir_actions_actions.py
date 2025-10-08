from odoo import api, models

class IrActionsActions(models.Model):
    _inherit = 'ir.actions.actions'

    @api.model_create_multi
    def create(self, vals):
        res = super(IrActionsActions, self).create(vals)
        action_data_obj = self.env['action.data']
        for record in res:
            action_data_obj.create({'name':record.name,'action_id':record.id})
        return res

    def unlink(self):
        action_data_obj = self.env['action.data']
        for record in self:
            action_data_obj.search([('action_id','=',record.id)]).unlink()
        return super(IrActionsActions, self).unlink()