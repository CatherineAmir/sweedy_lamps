# -*- coding: utf-8 -*-
{
    'name': "Purchase Letter of Credit",
    'summary': """Purchase Letter of Credit""",
    'author': "Mahmoud Naguib",
    "version": "13.0.1.0.0",
    "category": "account",
    "depends": ["account","purchase"],
    "data": [
        'security/ir.model.access.csv',
        'data/data.xml',
        'wizard/lc_amount_extend_wizard.xml',
        'wizard/lc_period_extend_wizard.xml',
        'views/purchase_letter_credit_type.xml',
        'views/purchase_letter_credit.xml',
        'views/account_move.xml',
        'views/account_payment.xml',

    ],
    "license": 'AGPL-3',
    'installable': True,
}
