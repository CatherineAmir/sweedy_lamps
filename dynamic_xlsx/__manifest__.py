# -*- coding: utf-8 -*-
{
    'name' : 'Xlsx support on Dynamic Financial Reports v13',
    'version' : '13.0',
    'summary': 'Xlsx Support module for dynamic reports for odoo v13.',
    'sequence': 15,
    'description': """
                    Xlsx Support module for dynamic reports for odoo v13.
                    It is a supporting module for account_dynamic_reports.
                    """,
    'category': 'Accounting/Accounting',
    'images': [],
    'depends': ['account_dynamic_reports','report_xlsx'],
    'data': ['wizard/wizard_inherit_view.xml'],
    'demo': [],
    'license': 'AGPL-3',
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
