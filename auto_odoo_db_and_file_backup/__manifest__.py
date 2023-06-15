# -*- coding: utf-8 -*-
#odoo13
{
    'name': "Automatic Backup (Google Drive, Dropbox, Amazon S3, FTP, SFTP, Local)",
	'category': 'Extra Tools',
	'version': '1.0', 
	
    'summary': 'Automatic Backup -(Google Drive, Dropbox, Amazon S3, FTP, SFTP, Local)',
    'description': "Automatic Backup -(Google Drive, Dropbox, Amazon S3, FTP, SFTP, Local)",
	'license': 'OPL-1',
    'price': 29.29,
	'currency': 'USD',
	
	'author': "Icon Technology",
    'website': "https://icontechnology.co.in",
    'support':  'team@icontechnology.in',
    'maintainer': 'Icon Technology',

	'images': ['static/description/auto-backup-odoo-v13.jpg',
	'static/description/auto-backup_screenshot.gif'],
	
    # any module necessary for this one to work correctly
    'depends': ['base','google_drive','mail'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/auto_backup_mail_templates.xml',
        'data/data.xml',
    ],
    'installable': True,
    'application': True,
}
