from odoo import fields, models, api, _
from lxml import etree


class RevokeButtonTab(models.Model):
    _name = 'revoke.button.tab'
    _description = 'Revoke Button Tab'

    access_right_mgmt_id = fields.Many2one('access.right.mgmt', 'Access Management')
    model_id = fields.Many2one('ir.model', string='Model', index=True, required=True, ondelete='cascade',compute="_compute_model_id",store=True,readonly=False)
    model_name = fields.Char(string='Model Name', related='model_id.model', readonly=False, store=True)

    btn_model_nodes_ids = fields.Many2many(
        'store.model.nodes',
        string='Revoke Button',
        domain="[('node_option','=','button')]",
        relation='revoke_button_tab_store_model_nodes_btn_rel',
        column1='revoke_button_tab_id',
        column2='store_node_btn_id'
    )
    
    page_model_nodes_ids = fields.Many2many(
        'store.model.nodes',
        string='Revoke Tab/Page',
        domain="[('node_option','=','page')]",
        relation='revoke_button_tab_store_model_nodes_page_rel',
        column1='revoke_button_tab_id',
        column2='store_node_page_id'
    )

    @api.depends('model_name')
    def _compute_model_id(self):
        for rec in self:
            model_id = self.env['ir.model'].search([('model','=',rec.model_name)]).id
            if model_id:
                rec.model_id = model_id

    def _store_btn_data(self, btn, smart_button=False, smart_button_string=False):
        # string_value is used in case of kanban view button store,
        string_value = 'string_value' in self._context.keys() and self._context['string_value'] or False

        store_model_button_obj = self.env['store.model.nodes']
        name = btn.get('string') or string_value
        if smart_button:
            name = smart_button_string
        store_model_button_obj.create({
            'model_id': self.model_id.id,
            'node_option': 'button',
            'attribute_name': btn.get('name'),
            'attribute_string': name,
            'button_type': btn.get('type'),
            'is_smart_button': smart_button,
        })

    def _get_smart_btn_string(self, btn_list, type=False):
        store_model_button_obj = self.env['store.model.nodes']

        def _get_span_text(span_list):
            name = ''
            for sp in span_list:
                if sp.text:
                    name = name + ' ' + sp.text
            name = name.strip()
            return name

        for btn in btn_list:
            name = ''
            field_list = btn.findall('field')
            if field_list:
                name = field_list[0].get('string')
            else:
                span_list = btn.findall('span')
                if span_list:
                    name = _get_span_text(span_list)
                else:
                    div_list = btn.findall('div')
                    if div_list:
                        span_list = div_list[0].findall('span')
                        if span_list:
                            name = _get_span_text(span_list)
            if not name:
                try:
                    name = btn.get('string')
                except:
                    pass
            if name and (type == 'object' or type == 'action'):
                domain = [('button_type', '=', btn.get('type')), ('attribute_string', '=', name),
                          ('model_id', '=', self.model_id.id), ('node_option', '=', 'button')]
                if type == 'object':
                    domain += [('attribute_name', '=', btn.get('name'))]
                if type == 'action':
                    domain += [('attribute_name', '=', btn.get('name'))]
                smart_button_id = store_model_button_obj.search(domain)
                if not smart_button_id:
                    self._store_btn_data(btn, smart_button=True, smart_button_string=name)
                else:
                    smart_button_id[0].is_smart_button = True

    @api.onchange('model_id')
    def _get_button(self):
        if self.model_id and self.model_name:
            store_model_nodes_obj = self.env['store.model.nodes']
            view_obj = self.env['ir.ui.view']
            view_list = ['form', 'tree', 'kanban']
            for view in view_list:
                for views in view_obj.search(
                        [('model', '=', self.model_name), ('type', '=', view), ('inherit_id', '=', False)]):
                    res = self.env[self.model_name].sudo().get_view(view_id=views.id, view_type=view)
                    doc = etree.XML(res['arch'])

                    object_button = doc.xpath("//button[@type='object']")
                    for btn in object_button:
                        string_value = btn.get('string')
                        if btn.get('name') and string_value:
                            domain = [('button_type', '=', btn.get('type')), ('attribute_string', '=', string_value),
                                      ('attribute_name', '=', btn.get('name')), ('model_id', '=', self.model_id.id),
                                      ('node_option', '=', 'button')]
                            if not store_model_nodes_obj.search(domain):
                                self.with_context(string_value=string_value)._store_btn_data(btn)

                    action_button = doc.xpath("//button[@type='action']")
                    for btn in action_button:
                        string_value = btn.get('string')
                        print("String value is -----------------",string_value)
                        if view == 'kanban' and not string_value:
                            try:
                                string_value = btn.text if not btn.text.startswith('\n') else False
                            except:
                                pass
                        if btn.get('name') and string_value:
                            domain = [('button_type', '=', btn.get('type')), ('attribute_string', '=', string_value),
                                      ('attribute_name', '=', btn.get('name')), ('model_id', '=', self.model_id.id),
                                      ('node_option', '=', 'button')]
                            if not store_model_nodes_obj.search(domain):
                                self.with_context(string_value=string_value)._store_btn_data(btn)

                    page_list = doc.xpath("//page")
                    if page_list:
                        for page in page_list:
                            if page.get('string'):
                                domain = [('attribute_string', '=', page.get('string')),
                                          ('model_id', '=', self.model_id.id), ('node_option', '=', 'page')]
                                if page.get('name'):
                                    domain += [('attribute_name', '=', page.get('name'))]
                                store_model_nodes_id = store_model_nodes_obj.search(domain, limit=1)
                                if not store_model_nodes_id:
                                    store_model_nodes_obj.create({
                                        'model_id': self.model_id.id,
                                        'attribute_name': page.get('name'),
                                        'attribute_string': page.get('string'),
                                        'node_option': 'page',
                                    })
