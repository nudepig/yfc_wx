# -*- coding: utf-8 -*-
{
    'name': "yfc_wx",

    'summary': """
        企业微信消息流推送""",

    'description': """
        企业微信
    """,

    'author': "auroral",
    'website': "http://www.auroral.top",
    'images': ['static/description/icon.png'],

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','website'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/wx_init_data.xml',

        'views/res_partner_views.xml',

        'views/wx_corp_config_views.xml',
        'views/wx_corpuser_views.xml',
        'views/wx_confirm_views.xml',
        'views/parent_menus.xml',


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}