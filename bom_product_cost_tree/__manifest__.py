# -*- coding: utf-8 -*-
{
    'name': "BOM Product Cost In TreeView",

    'summary': """
        Show product cost in BOM tree view""",

    'description': """
        Long description of module's purpose
    """,

    'author': "   ",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'mrp',
                ],

    # always loaded
    'data': [
        'views/bom_views.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
