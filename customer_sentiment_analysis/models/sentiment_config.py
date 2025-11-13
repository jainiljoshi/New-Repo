# -*- coding: utf-8 -*-
from odoo import models, fields

class SentimentConfiguration(models.Model):
    _name = 'sentiment.config'
    _description = 'Sentiment Analysis Configuration'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, tracking=True)
    api_provider = fields.Selection([
        ('openai', 'OpenAI'),
        ('google', 'Google Cloud NLP'),
        ('aws', 'AWS Comprehend'),
        ('azure', 'Azure Text Analytics'),
        ('custom', 'Custom API'),
    ], default='custom', required=True, tracking=True)
    api_key = fields.Char()
    api_endpoint = fields.Char()
    auto_analyze = fields.Boolean(string='Auto-Analyze', default=False)
    sentiment_threshold = fields.Float(string='Action Threshold', default=-1.0)
    notify_negative = fields.Boolean(default=True)
    notification_users = fields.Many2many('res.users', string='Notify Users')
    company_id = fields.Many2one('res.company', default=lambda s: s.env.company, required=True)
    active = fields.Boolean(default=True)
