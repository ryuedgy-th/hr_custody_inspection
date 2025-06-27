# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class CustodyProperty(models.Model):
    _inherit = 'custody.property'

    # Inspection fields
    inspection_ids = fields.One2many(
        'device.inspection',
        'property_id',
        string='Inspections',
        help='All inspections performed on this property'
    )
    inspection_count = fields.Integer(
        string='Inspection Count',
        compute='_compute_inspection_count',
        help='Number of inspections for this property'
    )
    last_inspection_date = fields.Datetime(
        string='Last Inspection Date',
        compute='_compute_last_inspection_date',
        store=True,
        help='Date of the most recent inspection'
    )
    last_inspection_state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Last Inspection Status',
       compute='_compute_last_inspection_date',
       store=True,
       help='Status of the most recent inspection')

    @api.depends('inspection_ids')
    def _compute_inspection_count(self):
        """Compute the number of inspections for this property"""
        for record in self:
            record.inspection_count = len(record.inspection_ids)

    @api.depends('inspection_ids.inspection_date')
    def _compute_last_inspection_date(self):
        """Compute the date and status of the most recent inspection"""
        for record in self:
            latest_inspection = record.inspection_ids.filtered(
                lambda x: x.inspection_date
            ).sorted('inspection_date', reverse=True)[:1]
            
            if latest_inspection:
                record.last_inspection_date = latest_inspection.inspection_date
                record.last_inspection_state = latest_inspection.state
            else:
                record.last_inspection_date = False
                record.last_inspection_state = False

    def action_create_inspection(self):
        """Action to create a new device inspection for this property"""
        self.ensure_one()
        
        # Create new inspection with this property
        inspection = self.env['device.inspection'].create({
            'property_id': self.id,
        })
        
        return {
            'name': _('Device Inspection'),
            'type': 'ir.actions.act_window',
            'res_model': 'device.inspection',
            'view_mode': 'form',
            'res_id': inspection.id,
            'target': 'current',
            'context': {
                'default_property_id': self.id,
                'form_view_initial_mode': 'edit',
            }
        }
    
    def action_view_inspections(self):
        """Action to view all inspections for this property"""
        self.ensure_one()
        
        action = self.env['ir.actions.act_window']._for_xml_id(
            'hr_custody_inspection.action_device_inspection'
        )
        
        if len(self.inspection_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.inspection_ids.id,
            })
        else:
            action.update({
                'domain': [('property_id', '=', self.id)],
                'context': {
                    'default_property_id': self.id,
                    'search_default_property_id': self.id,
                }
            })
            
        return action