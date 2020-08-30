# See LICENSE file for full copyright and licensing details.

{
    'name': 'Purchase Order Three Level Approval',
    'version': '13.0.0.1.0',
    'license': 'AGPL-3',
    'category': 'Purchases',
    'summary': 'Purchase Order approval : Purchase Manager Approval,\
    Finance Manager Approval,\
    CEO / Director Approval',
    'description': """
Three level approval of Purchase Order
""",
    'author': 'ERP Labz',
    'maintainer': 'ERP Labz',
    'website': 'http://erplabz.com/',
    'depends': ['purchase', 'account'],
    'data': [
        'security/security.xml',
        'data/mail_template_data.xml',
        'wizard/po_refuse_reason_view.xml',
        'views/res_company_view.xml',
        'views/purchase_views.xml',
        'views/res_config_views.xml',
    ],
    'images': ['static/description/conver.jpg'],
    'installable': True,
    'price': 50,
    'currency': 'EUR',
    'application': False,
    'auto_install': False,
}
