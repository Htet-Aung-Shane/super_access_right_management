{
    "name": "Super Access Right",
    "description": "Access Right Management System Developed by MT Tech",
    "category": "Customizations",
    "author": "MT Tech",
    'license': 'OPL-1',
    'application': True,
    'installable': True,
    "auto_install": False,
    "version": "18.0.1.0.0",
    "price": 120.00,
    "currency": "USD",
    'depends': ['web', 'base'],
    "data": [
        'security/ir.model.access.csv',
        'security/access_super_access_right_mgmt.xml',
        'views/access_right_mgmt.xml',
        'views/res_users.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/super_access_right_management/static/src/js/action_menu.js',
        ],

    },
    'images': [
        'static/description/banner.png',
        'static/description/screenshot1.png',
        'static/description/screenshot2.png',
        'static/description/screenshot3.png',
        'static/description/screenshot4.png',
        'static/description/screenshot5.png',
        'static/description/screenshot6.png',
        'static/description/screenshot7.png',
    ],
    'module_type': 'official',
    'post_init_hook': 'post_install_action_dup_hook'
}
