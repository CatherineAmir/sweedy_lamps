# -*- coding: utf-8 -*-
{
    'name': "Discount Cycle",

    'summary': """
        """,

    'description': """
        
    """,

    'author': "Mohamed Fouad",
    'website': "http://www.linkedin.com/in/mfhm95",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale',],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/groups.xml',
        'views/views.xml',
        'views/customers.xml',
        'views/templates.xml',
        'views/res_config_view.xml',
        'views/crons.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}