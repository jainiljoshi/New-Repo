# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class BulkSentimentWizard(models.TransientModel):
    _name = 'bulk.sentiment.wizard'
    _description = 'Bulk Sentiment Analysis Wizard'

    source_model = fields.Selection([
        ('crm.lead', 'CRM Leads'),
        ('mail.message', 'Email Messages'),
        ('helpdesk.ticket', 'Helpdesk Tickets'),
    ], required=True, default='crm.lead')
    date_from = fields.Date(required=True, default=fields.Date.context_today)
    date_to = fields.Date(required=True, default=fields.Date.context_today)
    partner_ids = fields.Many2many('res.partner', string='Customers')
    auto_assign = fields.Boolean(default=True)

    def action_analyze_bulk(self):
        self.ensure_one()
        domain = [('create_date', '>=', self.date_from), ('create_date', '<=', self.date_to)]
        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))
        records = self.env[self.source_model].search(domain)
        if not records:
            raise UserError(_('No records found for selected criteria.'))
        created_ids = []
        for rec in records:
            text = self._extract_text(rec)
            if not text:
                continue
            vals = {
                'partner_id': getattr(rec, 'partner_id', False) and rec.partner_id.id or False,
                'text_content': text,
                'source_type': self._map_source(self.source_model),
                'source_reference': getattr(rec, 'name', str(rec.id)),
            }
            if self.source_model == 'crm.lead':
                vals['crm_lead_id'] = rec.id
                if self.auto_assign and getattr(rec, 'user_id', False):
                    vals['assigned_user_id'] = rec.user_id.id
            s = self.env['sentiment.analysis'].create(vals)
            s.action_analyze_sentiment()
            created_ids.append(s.id)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Analyzed Records'),
            'res_model': 'sentiment.analysis',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', created_ids)],
        }

    def _extract_text(self, rec):
        if self.source_model == 'crm.lead':
            return f"{rec.name or ''}\n{rec.description or ''}"
        if self.source_model == 'mail.message':
            return rec.body or ''
        if self.source_model == 'helpdesk.ticket':
            return f"{rec.name or ''}\n{rec.description or ''}"
        return ''

    def _map_source(self, model):
        return {'crm.lead': 'crm', 'mail.message': 'email', 'helpdesk.ticket': 'helpdesk'}.get(model, 'manual')
