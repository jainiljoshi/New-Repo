# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging
_logger = logging.getLogger(__name__)

class SentimentAnalysis(models.Model):
    _name = 'sentiment.analysis'
    _description = 'Customer Sentiment Analysis'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True
    )
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True, index=True)
    text_content = fields.Text(string='Content', required=True, help='Text content to be analyzed')
    sentiment = fields.Selection([
        ('very_positive', 'Very Positive'),
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
        ('very_negative', 'Very Negative'),
    ], string='Sentiment', tracking=True, index=True)
    sentiment_score = fields.Float(string='Sentiment Score', digits=(16, 4),
                                   help='Score from -3.0 (very negative) to 3.0 (very positive)', tracking=True)
    confidence_level = fields.Float(string='Confidence %', digits=(5, 2),
                                    help='Model confidence percentage')
    emotions = fields.Selection([
        ('joy', 'Joy'), ('trust', 'Trust'), ('fear', 'Fear'), ('surprise', 'Surprise'),
        ('sadness', 'Sadness'), ('disgust', 'Disgust'), ('anger', 'Anger'), ('anticipation', 'Anticipation'),
    ], string='Primary Emotion')
    keywords = fields.Text(string='Keywords')
    aspect_analysis = fields.Text(string='Aspect-Based Analysis', help='JSON of aspect -> sentiment')
    analysis_notes = fields.Text(string='Analysis Notes')

    source_type = fields.Selection([
        ('email', 'Email'),
        ('crm', 'CRM Lead/Opportunity'),
        ('helpdesk', 'Helpdesk Ticket'),
        ('social_media', 'Social Media'),
        ('review', 'Product Review'),
        ('survey', 'Survey Response'),
        ('chat', 'Chat/Messaging'),
        ('manual', 'Manual Entry'),
    ], string='Source Type', required=True, tracking=True)
    source_reference = fields.Char(string='Source Reference')
    crm_lead_id = fields.Many2one('crm.lead', string='Related CRM Lead', index=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('analyzed', 'Analyzed'),
        ('reviewed', 'Reviewed'),
        ('actioned', 'Action Taken'),
        ('archived', 'Archived'),
    ], default='draft', required=True, tracking=True)
    priority = fields.Selection([('0','Low'),('1','Normal'),('2','High'),('3','Very High')],
                                default='1', tracking=True)
    action_required = fields.Boolean(string='Action Required', compute='_compute_action_required', store=True)
    assigned_user_id = fields.Many2one('res.users', string='Assigned To', tracking=True, index=True)
    analysis_date = fields.Datetime(string='Analysis Date', default=fields.Datetime.now, required=True)
    response_deadline = fields.Date(string='Response Deadline', compute='_compute_response_deadline', store=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda s: s.env.company)
    color = fields.Integer(string='Color Index', compute='_compute_color')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('sentiment.analysis') or _('New')
        return super().create(vals)

    @api.depends('sentiment', 'sentiment_score')
    def _compute_action_required(self):
        for rec in self:
            rec.action_required = (rec.sentiment in ('negative','very_negative')) or                                           (rec.sentiment_score is not None and rec.sentiment_score < -1.0)

    @api.depends('sentiment', 'analysis_date')
    def _compute_response_deadline(self):
        for rec in self:
            if rec.analysis_date:
                days = 1 if rec.sentiment == 'very_negative' else (2 if rec.sentiment == 'negative' else 7)
                # fields.Date.add expects a datetime.date object; using dateutils would be ideal but keep simple:
                try:
                    rec.response_deadline = (rec.analysis_date + fields.timedelta(days=days)).date()
                except Exception:
                    # fallback: false
                    rec.response_deadline = False
            else:
                rec.response_deadline = False

    @api.depends('sentiment')
    def _compute_color(self):
        cmap = {'very_positive': 10, 'positive': 9, 'neutral': 4, 'negative': 2, 'very_negative': 1}
        for rec in self:
            rec.color = cmap.get(rec.sentiment, 4)

    def action_analyze_sentiment(self):
        self.ensure_one()
        if not self.text_content:
            raise UserError(_('No content to analyze.'))
        # Placeholder for integration; replace with real provider call from config
        result = self._mock_sentiment(self.text_content)
        self.write({
            'sentiment': result.get('sentiment'),
            'sentiment_score': result.get('score'),
            'confidence_level': result.get('confidence'),
            'emotions': result.get('emotion'),
            'keywords': result.get('keywords'),
            'aspect_analysis': json.dumps(result.get('aspects', {})),
            'state': 'analyzed',
            'analysis_date': fields.Datetime.now(),
        })
        self.message_post(body=_('Sentiment analysis completed: %s') % (self.sentiment or '-'),
                          subtype_xmlid='mail.mt_note')
        return True

    def _mock_sentiment(self, text):
        # Replace with external API use as needed
        import random
        sentiments = ['very_positive', 'positive', 'neutral', 'negative', 'very_negative']
        s = random.choice(sentiments)
        sr = {'very_positive': (2.0,3.0),'positive':(1.0,2.0),'neutral':(-0.5,0.5),'negative':(-2.0,-1.0),'very_negative':(-3.0,-2.0)}
        score = random.uniform(*sr[s])
        return {
            'sentiment': s,
            'score': score,
            'confidence': random.uniform(70, 98),
            'emotion': random.choice(['joy','trust','fear','surprise','sadness','anger']),
            'keywords': ', '.join(text.split()[:5]),
            'aspects': {'product': 'neutral', 'service': 'positive', 'support': 'negative'}
        }

    def action_set_reviewed(self):
        self.write({'state': 'reviewed'})
        return True

    def action_set_actioned(self):
        self.write({'state': 'actioned'})
        return True

    def action_archive(self):
        self.write({'state': 'archived', 'active': False})
        return True
