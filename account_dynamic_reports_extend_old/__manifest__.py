{
    'name': 'All in one Dynamic Financial Reports v13',
    'version': '13',
    'summary': "General Ledger Trial Balance Ageing Balance Sheet Profit and Loss Cash Flow Dynamic",
    'sequence': 15,
    'description': """
                    Odoo 13 Full Accouning, Odoo 13 All in one Accouning, PDF Reports, XLSX Reports,
                    Dynamic View, Drill down, Clickable, Pdf and Xlsx package, Odoo 13 Accounting,
                    Full Account Reports, Complete Accounting Reports, Financial Report for Odoo 13,
                    Financial Reports, Excel reports, Financial Reports in Excel, Ageing Report,
                    General Ledger, Partner Ledger, Trial Balance, Balance Sheet, Profit and Loss,
                    Financial Report Kit, Cash Flow Statements, Cash Flow Report, Cash flow, Dynamic reports,
                    Dynamic accounting, Dynamic financial
                    """,
    'category': 'Accounting/Accounting',
    'maintainer': '',
    'website': '',
    'depends': [
        'account_dynamic_reports',
        'dynamic_xlsx',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/general_ledger.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
