# -*- coding: utf-8 -*-
# License: Odoo Proprietary License v1.0

{
    'name': 'Odoo13 Accounting Excel Reports',
    'version': '13.0.1.0.2',
    'category': 'Invoicing Management',
    'summary': 'Accounting Reports In Excel For Odoo 13',
    'sequence': '5',
    'live_test_url': 'https://www.youtube.com/watch?v=pz83Q9dobOM',
    'author': 'Odoo Mates',
    'company': 'Odoo Mates',
    'maintainer': 'Odoo Mates',
    'support': 'odoomates@gmail.com',
    'license': "OPL-1",
    'price': 20.00,
    'currency': 'USD',
    'website': '',
    'depends': ['accounting_pdf_reports'],
    'images': ['static/description/banner.png'],
    'demo': [],
    'data': [
        'reports/report.xml',
        'wizards/account_excel_reports.xml',
        'views/templates.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}
