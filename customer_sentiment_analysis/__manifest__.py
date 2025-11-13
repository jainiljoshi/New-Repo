# -*- coding: utf-8 -*-
{
    'name': 'Customer Sentiment Analysis',
    'version': '1.0.0',
    'category': 'CRM/Analytics',
    'summary': 'Backend module for customer sentiment analysis and monitoring',
    'description': 'Backend-only implementation with models, views, security, wizards; OWL assets included but disabled for now.',
    'author': 'Your Company',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'crm',
        'web',
    ],
    'data': [
        'security/sentiment_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/sentiment_menu.xml',
        'views/sentiment_analysis_views.xml',
        'views/sentiment_config_views.xml',
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'customer_sentiment_analysis/static/src/css/sentiment_styles.css',
    #         'customer_sentiment_analysis/static/src/js/sentiment_dashboard.js',
    #         'customer_sentiment_analysis/static/src/xml/sentiment_templates.xml',
    #     ],
    # },
    'installable': True,
    'application': True,
    'auto_install': False,
}
