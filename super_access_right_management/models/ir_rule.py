import psycopg2
from odoo import api, fields, models, tools, _
from odoo.tools import config
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class IrRule(models.Model):
    _inherit = 'ir.rule'

    @api.model
    @tools.conditional(
        'xml' not in config['dev_mode'],
        tools.ormcache(
            'self.env.uid',
            'self.env.su',
            'model_name',
            'mode','tuple(self._compute_domain_context_values())'
        ),
    )
    def _compute_domain(self, model_name, mode="read"):
        """Custom access rule domain logic integrated with access_right_mgmt module."""
        res = super()._compute_domain(model_name, mode)
        read_value = True

        #Check if the custom access management module is installed
        try:
            self._cr.execute("SELECT state FROM ir_module_module WHERE name=%s", ['access_right_mgmt'])
            data = self._cr.fetchone() or False
        except Exception:
            self._cr.rollback()
            data = None

        # Check if any module is being upgraded/installed/removed
        try:
            self._cr.execute(
                "SELECT id FROM ir_module_module WHERE state IN ('to upgrade', 'to remove', 'to install')"
            )
            all_data = self._cr.fetchone() or False
        except Exception:
            self._cr.rollback()
            all_data = None

        #Skip rule enforcement if module not installed
        if data and data[0] != 'installed':
            read_value = False

        #  Models to exclude from access filtering
        model_list = [
            'mail.activity', 'res.users.log', 'res.users', 'mail.channel',
            'mail.alias', 'bus.presence', 'res.lang'
        ]

        # Only proceed if valid user and environment
        if self.env.user.id and read_value and not all_data:
            if model_name not in model_list:
                try:
                    self._cr.execute("SELECT id FROM ir_model WHERE model=%s", [model_name])
                    model_numeric_id = self._cr.fetchone()
                    model_numeric_id = model_numeric_id and model_numeric_id[0] or False
                    if model_numeric_id and isinstance(model_numeric_id, int) and self.env.user:
                        self._cr.execute("""
                            SELECT dm.id
                            FROM access_domain AS dm
                            WHERE dm.model_id=%s AND dm.access_right_mgmt_id IN (
                                SELECT am.id FROM access_right_mgmt AS am
                                WHERE active='t' AND am.id IN (
                                    SELECT amusr.access_right_mgmt_id
                                    FROM access_management_users_rel AS amusr
                                    WHERE amusr.user_id=%s
                                )
                            )
                        """, [model_numeric_id, self.env.user.id])
                        rows = self._cr.fetchall()
                    else:
                        rows = []
                except Exception:
                    self._cr.rollback()
                    rows = []

                access_domain_ids = self.env['access.domain'].browse([r[0] for r in rows])

                if access_domain_ids:
                    domain_list = []

                    #  Special handling for partner restriction
                    if model_name == 'res.partner':
                        try:
                            self._cr.execute("SELECT partner_id FROM res_users")
                            partner_ids = [r[0] for r in self._cr.fetchall()]
                            domain_list = [[('id', 'in', partner_ids)]]
                        except Exception:
                            self._cr.rollback()

                    #Use recursion-safe eval context
                    eval_context = {
                        'uid': self.env.uid,
                        'user': self.env.user.sudo(),
                        'time': tools.safe_eval.time,
                        'datetime': tools.safe_eval.datetime,
                        'context': dict(self.env.context),
                    }

                    # Build dynamic domain list
                    for access in access_domain_ids.sudo():
                        dom = safe_eval(access.domain, eval_context) if access.domain else []
                        if dom:
                            dom = expression.normalize_domain(dom)
                            for dom_tuple in dom:
                                if isinstance(dom_tuple, tuple):
                                    left_value, operator_value, right_value = dom_tuple
                                    left_user = False
                                    model_string = model_name

                                    #  Safely traverse relation fields
                                    for field in left_value.split('.'):
                                        model_obj = self.env[model_string]
                                        fields_info = model_obj.fields_get()

                                        #  Skip if field not present
                                        if field not in fields_info:
                                            continue

                                        field_type = fields_info[field]['type']
                                        if field_type in ['many2one', 'many2many', 'one2many']:
                                            model_string = fields_info[field]['relation']
                                            if model_string == 'res.users':
                                                left_user = True

                                    # Replace placeholder 0 with current user ID
                                    if left_user and operator_value in ['in', 'not in']:
                                        if isinstance(right_value, list) and 0 in right_value:
                                            right_value[right_value.index(0)] = self.env.user.id
                            domain_list.append(dom)

                    # Combine all domains if present
                    if domain_list:
                        return expression.OR(domain_list)

        #  Default return (use original rule domain)
        return res
