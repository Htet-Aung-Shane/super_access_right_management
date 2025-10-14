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
                actions_and_prints += access.mapped(
                    'report_action_ids.action_id').ids
                actions_and_prints += access.mapped(
                    'server_action_ids.action_id').ids
            for view in ['list', 'form']:
                if view in res['views'].keys():
                    if 'toolbar' in res['views'][view].keys():
                        if 'print' in res['views'][view]['toolbar'].keys():
                            prints = res['views'][view]['toolbar']['print'][:]
                            for pri in prints:
                                if pri['id'] in actions_and_prints:
                                    res['views'][view]['toolbar']['print'].remove(
                                        pri)
                        if 'action' in res['views'][view]['toolbar'].keys():
                            action = res['views'][view]['toolbar']['action'][:]
                            for act in action:
                                if act['id'] in actions_and_prints:
                                    res['views'][view]['toolbar']['action'].remove(
                                        act)
        return res

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        res = super().get_view(view_id, view_type, **options)
        access_management_obj = self.env['access.right.mgmt']
        doc = etree.XML(res['arch'])
        if view_type == 'form':
            self.form_access_right_management(res['model'], doc)
            res['arch'] = etree.tostring(doc, encoding='unicode')

            # hide chatter
            if self.revoke_chatter_access_right_management(res['model'], access_management_obj, doc):
                res['arch'] = etree.tostring(doc, encoding='unicode')
            # hide field
            if self.hide_field_access_right_management(res['model'], doc, doc_type='form'):
                res['arch'] = etree.tostring(doc, encoding='unicode')
            # remove external link
            if self.access_external_link_management(res['model'], doc):
                res['arch'] = etree.tostring(doc, encoding='unicode')
            # access_page
            if self.page_access_right_management(res['model'], doc):
                res['arch'] = etree.tostring(doc, encoding='unicode')
            # button_page
            if self.button_access_right_management(res['model'], doc):
                res['arch'] = etree.tostring(doc, encoding='unicode')

        if self.readonly_access_right_management(access_management_obj, doc):
            res['arch'] = etree.tostring(
                doc, encoding='unicode').replace('&amp;quot;', '&quot;')
        else:
            doc = self.action_access_right_management(res['model'], doc, doc_type=view_type)
            res['arch'] = etree.tostring(doc, encoding='unicode')

        return res

    def readonly_access_right_management(self, access_management_obj, doc=None):
        readonly_access_id = access_management_obj.search(
            [('active', '=', True), ('user_ids', 'in', self.env.user.id),
             ('is_readonly', '=', True)])
        if readonly_access_id:
            doc.attrib.update(
                {'create': 'false', 'delete': 'false', 'edit': 'false'})
            return True

        return False

    def revoke_chatter_access_right_management(self, model, access_management_obj, doc=None):
        if access_management_obj.search(
            [('active', '=', True), ('user_ids', 'in', self.env.user.id),
             ('revoke_chatter', '=', True)],
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

    def access_external_link_management(self, model, doc=None):
        access_fields_recs = self.env['revoke.field'].search([
            ('access_right_mgmt_id.user_ids', 'in', self.env.user.id),
            ('access_right_mgmt_id.active', '=', True),
            ('model_id.model', '=', model), ('is_revoke_external_link', '=', True)])
        if access_fields_recs:
            for field in access_fields_recs.mapped('field_ids'):
                if field.ttype in ['many2many', 'many2one']:
                    for field_ele in doc.xpath("//field[@name='" + field.name + "']"):
                        options = 'options' in field_ele.attrib.keys(
                        ) and field_ele.attrib['options'] or "{}"
                        options = ast.literal_eval(options)
                        options.update(
                            {'no_create': True, 'no_create_edit': True, 'no_open': True})
                        field_ele.attrib.update({'options': str(options)})
            return True
        return False

    def page_access_right_management(self, model=None, doc=None):
        access_fields_recs = self.env['revoke.button.tab'].search([
            ('access_right_mgmt_id.user_ids', 'in', self.env.user.id),
            ('access_right_mgmt_id.active', '=', True),
            ('model_id.model', '=', model)])
        if access_fields_recs:
            for access_fields_rec in access_fields_recs:
                for page in access_fields_rec.mapped('page_model_nodes_ids'):
                    for field_ele in doc.xpath("//page[@name='" + page.attribute_name + "']"):
                        field_ele.set('invisible', '1')
                return True
        return False

    def button_access_right_management(self, model=None, doc=None):
        access_fields_recs = self.env['revoke.button.tab'].search([
            ('access_right_mgmt_id.user_ids', 'in', self.env.user.id),
            ('access_right_mgmt_id.active', '=', True),
            ('model_id.model', '=', model)])
        if access_fields_recs:
            for access_fields_rec in access_fields_recs:
                for button in access_fields_rec.mapped('btn_model_nodes_ids'):
                    for field_ele in doc.xpath("//button[@name='" + button.attribute_name + "']"):
                        field_ele.set('invisible', '1')
                return True
        return False

    def hide_field_access_right_management(self, model=None, doc=None, doc_type='form'):
        access_fields_recs = self.env['revoke.field'].search([
            ('access_right_mgmt_id.user_ids', 'in', self.env.user.id),
            ('access_right_mgmt_id.active', '=', True),
            ('model_id.model', '=', model)])
        if access_fields_recs:
            for access_fields_rec in access_fields_recs:
                for field in access_fields_rec.mapped('field_ids'):
                    for field_ele in doc.xpath("//field[@name='" + field.name + "']"):
                        if access_fields_rec.is_invisible:
                            if doc_type == 'form':
                                field_ele.set('invisible', '1')
                            else:
                                field_ele.set('column_invisible', '1')
                        if access_fields_rec.is_readonly:
                            field_ele.set('readonly', '1')
                        if access_fields_rec.is_required:
                            field_ele.set('required', '1')
                return True
        return False

    def action_access_right_management(self, model, doc=None, doc_type='form'):
        access_revoke_action_model_ids = self.env['revoke.action'].search([
            ('access_right_mgmt_id.user_ids', 'in', self.env.user.id),
            ('access_right_mgmt_id.active', '=', True),
            ('model_id.model', '=', model)])
        if access_revoke_action_model_ids:
            delete = 'true'
            edit = 'true'
            create = 'true'
            duplicate = 'true'
            for revoke_action_ids in access_revoke_action_model_ids:
                if revoke_action_ids.revoke_create:
                    create = 'false'
                if revoke_action_ids.revoke_edit:
                    edit = 'false'
                if revoke_action_ids.revoke_delete:
                    delete = 'false'
                if revoke_action_ids.is_readonly:
                    create, delete, edit = 'false', 'false', 'false'
                if revoke_action_ids.revoke_duplicate:
                    duplicate = 'false'
            if doc_type == 'form':
                doc.attrib.update(
                    {'create': create, 'delete': delete, 'edit': edit, 'duplicate': duplicate})

        return doc

    def form_access_right_management(self, model=None, doc=None):
        model_of_all_fields = self.env[model]._fields
        one2many_fields = set(
            filter(lambda x: isinstance(model_of_all_fields[x], odoo.fields.One2many),
                   model_of_all_fields))  # - unused
        if one2many_fields:
            restrict_mo2m_model = dict()
            for o2m in one2many_fields:
                restrict_mo2m_model[o2m] = model_of_all_fields[o2m]._related_comodel_name
            restrict_o2m_model = self.env['revoke.action'].search([
                ('access_right_mgmt_id.user_ids', 'in', self.env.user.id),
                ('access_right_mgmt_id.active', '=', True),
                ('model_id.model', 'in', list(restrict_mo2m_model.values()))
            ])
            if restrict_o2m_model:
                for key, value in restrict_mo2m_model.items():
                    for rest in restrict_o2m_model:
                        if rest.model_id.model == value:
                            for f in doc.xpath("//field[@name='" + key + "']//list"):
                                options = dict()
                                if rest.restrict_create:
                                    options['create'] = '0'
                                if rest.restrict_edit:
                                    options['edit'] = '0'
                                if rest.restrict_delete:
                                    options['delete'] = '0'
                                f.attrib.update(options)

            # access_one_2_many_field
            for o2m_model in list(restrict_mo2m_model.values()):
                self.hide_field_access_right_management(
                    o2m_model, doc, doc_type='list')
                self.action_access_right_management(o2m_model, doc, doc_type='list')
