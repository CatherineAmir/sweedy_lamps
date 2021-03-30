# -*- coding: utf-8 -*-
{
    'name': 'POS Kitchen screen',
    'version': '13.0.1.0',
    'category': 'Point of Sale',
    'website': 'https://www.boraq-group.com',
    'price': 20.0,
    'currency': 'EUR',
    'summary': "A Screen for kitchen staff.",
    'description': "POS kitchen Screen shows orders and their state to Cook and Manager",
    'author': "Boraq-Group",
    'depends': ['point_of_sale','bus','pos_restaurant'],
    'data': [
        'views/res_users_view.xml',
        'views/pos_kitchen_screen.xml',
        'views/kitchen_screen_view.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False
}
