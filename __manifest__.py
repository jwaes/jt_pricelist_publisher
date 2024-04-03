# -*- coding: utf-8 -*-
{
    'name': "jt_pricelist_publisher",

    'summary': "Pricelist publisher",

    'description': "",

    'author': "jaco tech",
    'website': "https://jaco.tech",
    "license": "AGPL-3",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.6',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','product', 'web','jt_product_properties','jt_product_repeat'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/product_pricelist_views.xml',
        'views/publication_views.xml',
        'views/publication_block_views.xml',
        'views/ir_actions_report.xml',
        # 'views/templates.xml',
        'report/pricelist_publication_reports.xml',
        'report/pricelist_publication_report_templates.xml',
        'wizard/pricelist_publishing_wizard.xml',
    ],

    'assets': {
        'web.report_assets_common': [
            'jt_pricelist_publisher/static/src/css/repeat_pricelist.css',
            'jt_pricelist_publisher/report/assets/layout_pricelist.scss',
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "external_dependencies": {
        "python": [  # Python third party libraries required for module
            "PyPDF2",
        ]
    },    
}
