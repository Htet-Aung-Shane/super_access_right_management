{
    "name": "Super Access Right",
    "description": "Access Right Management System Developed by MT Tech",
    "category": "Customizations",
    "author": "MT Tech",
    'license': 'OPL-1',
    'application': True,
    'installable': True,
    "auto_install": False,
    'depends': ['web', 'base'],
    "data": [
        'security/ir.model.access.csv',
        'views/access_right_mgmt.xml',
        'views/res_users.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/super_access_right_management/static/src/js/action_menu.js',
        ],

    },
    'module_type': 'official',
    'post_init_hook': 'post_install_action_dup_hook'
}
