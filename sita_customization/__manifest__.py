# -*- coding: utf-8 -*-
{
    'name': "sita_customization",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','stock_card_report','stock_account',"report_xlsx"],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'reports/stock_card_pdf.xml',
        'views/stock_quant_tree.xml',
        'data/inventory_report_paper_format.xml',
        'reports/inventory_report_pdf.xml',
        'reports/production_orders_report_pdf.xml',
        'reports/sales_account_profitability_report_pdf.xml',
        'reports/report_data.xml',
        'wizards/inventory_report_wizard.xml',
        'reports/inventory_report_html.xml',
        'wizards/manifacturing_order_report_wizard.xml',
        'reports/production_orders_report_pdf.xml',
        'wizards/sales_account_report_wizard.xml',
        'views/account_move_line.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
