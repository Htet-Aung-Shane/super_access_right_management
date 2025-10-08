from odoo import api, SUPERUSER_ID
from . import models
from . import controllers


def post_install_action_dup_hook(env):
    action_data_obj = env['action.data']
    for action in env['ir.actions.actions'].search([]):
        action_data_obj.create({'name': action.name, 'action_id': action.id})
