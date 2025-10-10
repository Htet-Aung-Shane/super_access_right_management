from odoo import models,api, SUPERUSER_ID, _
from lxml import etree

class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    def _postprocess_tag_field(self, node, name_manager, node_info):
        self.env.registry.clear_cache()
        res = super(IrUiView, self)._postprocess_tag_field(
            node, name_manager, node_info)
        self._access_right_mgmt_check_view_access_fields(node, name_manager, node_info)
        return res
    
    def _access_right_mgmt_check_view_access_fields(self, node, name_manager, node_info):
        
        hide_field_obj = self.env['revoke.field'].sudo()
        if node.tag == 'field' or node.tag == 'label':
            for hide_field in hide_field_obj.search(
                    [('model_id.model', '=', name_manager.model._name),
                     ('access_right_mgmt_id.active', '=', True),
                     ('access_right_mgmt_id.user_ids',
                      'in', [self.env.user.id])
                     ]):
                for field_id in hide_field.field_ids:
                    if (node.tag == 'field' and node.get('name') == field_id.name) or (
                            node.tag == 'label' and 'for' in node.attrib.keys() and node.attrib[
                                'for'] == field_id.name):

                        if hide_field.is_invisible:
                            node.set('invisible', '1')
                        if hide_field.is_readonly:
                            node.set('readonly', '1')
                        if hide_field.is_required:
                            node.set('required', '1')