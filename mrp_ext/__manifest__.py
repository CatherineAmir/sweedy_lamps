# -*- coding: utf-8 -*-
{
    'name': "EXTEND MRP",

    'summary': """
        EXTEND MRP""",

    'description': """
        EXTEND MRP
    """,

    'author': 'Saad El Wardany',
    'website': 'https://www.facebook.com/saad.wardany.1',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'HR',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mrp'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/mrp.xml',
    ],
    # only loaded in demonstration mode
}