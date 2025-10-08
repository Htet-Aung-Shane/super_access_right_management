from odoo.addons.web.controllers.home import Home
from odoo.http import request
from odoo import http


class Home(Home):

    @http.route()
    def web_client(self, s_action=None, **kw):
        user = request.session.uid
        if kw.get('debug') and kw.get('debug') != "0":
            access_management = request.env['access.right.mgmt'].sudo().search(
                [('active', '=', True), ('revoke_developer_mode', '=', True), ('user_ids', 'in', user)])
            if access_management:
                return request.redirect('/odoo?debug=0')
            
        res= super().web_client(s_action, **kw)

        # update_view
        return res
