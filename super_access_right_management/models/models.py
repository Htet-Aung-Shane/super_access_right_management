import odoo.fields
from odoo import api, fields, models
from lxml import etree
import ast


class BaseModel(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def get_views(self, views, options=None):
        res = super().get_views(views, options)
        if 'views' in res.keys():
            actions_and_prints = []
            for access in self.env['revoke.action'].search(
                    [('access_right_mgmt_id', 'in', self.env.user.access_rights_mgmt_ids.ids),
                     ('model_id.model', '=', self._name)]):
                actions_and_prints += access.mapped('report_action_ids.action_id').ids
                actions_and_prints += access.mapped('server_action_ids.action_id').ids
            for view in ['list', 'form']:
                if view in res['views'].keys():
                    if 'toolbar' in res['views'][view].keys():
                        if 'print' in res['views'][view]['toolbar'].keys():
                            prints = res['views'][view]['toolbar']['print'][:]
                            for pri in prints:
                                if pri['id'] in actions_and_prints:
                                    res['views'][view]['toolbar']['print'].remove(pri)
                        if 'action' in res['views'][view]['toolbar'].keys():
                            action = res['views'][view]['toolbar']['action'][:]
                            for act in action:
                                if act['id'] in actions_and_prints:
                                    res['views'][view]['toolbar']['action'].remove(act)
        return res

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        res = super().get_view(view_id, view_type, **options)
        access_management_obj = self.env['access.right.mgmt']
        doc = etree.XML(res['arch'])
        if view_type == 'form':
            # hide chatter
            if self.revoke_chatter_access_right_management(res['model'], access_management_obj,doc):
                res['arch'] = etree.tostring(doc, encoding='unicode')

        if self.readonly_access_right_management(access_management_obj, doc):
            res['arch'] = etree.tostring(doc, encoding='unicode').replace('&amp;quot;', '&quot;')

        return res

    def readonly_access_right_management(self,access_management_obj, doc=None):
        readonly_access_id = access_management_obj.search(
            [('active', '=', True), ('user_ids', 'in', self.env.user.id),
             ('is_readonly', '=', True)])
        if readonly_access_id:
            doc.attrib.update({'create': 'false', 'delete': 'false', 'edit': 'false'})
            return True
        
        return False

    def revoke_chatter_access_right_management(self,model,access_management_obj, doc=None):
        if access_management_obj.search(
                    [('active', '=', True), ('user_ids', 'in', self.env.user.id), ('revoke_chatter', '=', True)],
                    limit=1).id:
                chatter = doc.xpath("//chatter")
                if chatter:
                    for ch in chatter:
                        ch.getparent().remove(ch)
                        return True

        else:            
            access_revoke_action_model_ids = self.env['revoke.action'].search([
                    ('access_right_mgmt_id.user_ids', 'in', self.env.user.id),
                    ('access_right_mgmt_id.active', '=', True),
                    ('model_id.model', '=', model)])
            if access_revoke_action_model_ids:
                for access_revoke_action_model_id in access_revoke_action_model_ids:
                    if access_revoke_action_model_id.revoke_chatter:
                        chatter = doc.xpath("//chatter")
                        if chatter:
                            for ch in chatter:
                                ch.getparent().remove(ch)
                                return True

        return False