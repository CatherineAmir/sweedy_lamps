
{
    'name' : 'All in one Dynamic Financial Reports v13',
    'version' : '13',
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
    'depends': ['account', 'sale_management'],
    'data': [
             'security/ir.model.access.csv',
             'data/data_financial_report.xml',

             'views/views.xml',
             'views/res_company_view.xml',

             'views/general_ledger_view.xml',
             'views/partner_ledger_view.xml',
             'views/trial_balance_view.xml',
             'views/partner_ageing_view.xml',
             'views/financial_report_view.xml',

             'wizard/general_ledger_view.xml',
             'wizard/partner_ledger_view.xml',
             'wizard/trial_balance_view.xml',
             'wizard/partner_ageing_view.xml',
             'wizard/financial_report_view.xml',
             ],
    'demo': [],
    'qweb': ['static/src/xml/view.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
