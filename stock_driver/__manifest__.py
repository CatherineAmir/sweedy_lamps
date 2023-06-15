# -*- coding: utf-8 -*-
{
    'name': "Stock Driver",
    'summary': """Stock Driver""",
    'author': "Mahmoud Naguib",
    "version": "13.0.1.0.0",
    "category": "stock",
    "depends": ["stock","sale_stock"],
    "data": [
        'security/ir.model.access.csv',
        'views/stock_picking.xml',
        'views/templates.xml',
        'views/product_product.xml',
        'views/sale_order.xml',
    ],
    "license": 'AGPL-3',
    'installable': True,
}
