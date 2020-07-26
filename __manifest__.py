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
    'category': 'yfc',
    'version': '0.1',
    'application': True,

    # any module necessary for this one to work correctly
    'depends': ['base','website','website_sale','account','auth_oauth'],

    # always loaded
    'data': [
        'data/auth_oauth_data.xml',
        'views/inherit_web_login.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
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