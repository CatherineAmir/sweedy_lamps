# -*- coding: utf-8 -*-
{
    'name': "Add fields to Invoice report",

    'summary': """
       """,

    'author': "Ahmed Hegazy",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/template.xml',
    ],
    # only loaded in demonstration mode
   
}
