# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class InspectionWizard(models.TransientModel):
    _name = 'inspection.wizard'
    _description = 'Create Inspection Wizard'

    property_id = fields.Many2one(
        'custody.property',
        string='Property',
        required=True,
        help="Asset/Property to be inspected"
    )
    inspection_type_id = fields.Many2one(
        'device.inspection.type',
        string='Inspection Type',
        required=True,
        help="Type of inspection to be performed"
    )
    notes = fields.Text(
        string='Notes',
        help="Initial notes for the inspection"
    )

    @api.model
    def default_get(self, fields_list):
        """Set default values from context"""
        res = super(InspectionWizard, self).default_get(fields_list)
        if self.env.context.get('active_model') == 'custody.property':
            property_id = self.env.context.get('active_id')
            if property_id:
                res['property_id'] = property_id
        return res

    def action_create_inspection(self):
        """Create a new inspection and open its form view"""
        self.ensure_one()
        
        # Create new inspection
        inspection = self.env['device.inspection'].create({
            'property_id': self.property_id.id,
            'inspection_type_id': self.inspection_type_id.id,
            'notes': self.notes,
        })
        
        # Return action to open the created inspection
        form_view = self.env.ref('hr_custody_inspection.device_inspection_view_form_new')
        
        return {
            'name': _('Device Inspection'),
            'type': 'ir.actions.act_window',
            'res_model': 'device.inspection',
            'view_mode': 'form',
            'res_id': inspection.id,
            'views': [(form_view.id, 'form')],
            'target': 'current',
            'context': {'form_view_initial_mode': 'edit'},
        } 