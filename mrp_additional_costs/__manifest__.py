# -*- coding: utf-8 -*-
{
    'name': "MRP Additional Costs",
    'summary': """MRP Additional Costs""",
    'author': "Mahmoud Naguib",
    "version": "13.0.1.0.0",
    "category": "Manufacturing",
    "depends": ["mrp","mrp_account_enterprise"],
    "data": [
        'security/security.xml',
        'views/templates.xml',
        'views/mrp_routing_workcenter.xml',
        'views/cost_structure_report.xml',
        'views/mrp_report_bom_structure.xml',
    ],
    "license": 'AGPL-3',
    'installable': True,
}
