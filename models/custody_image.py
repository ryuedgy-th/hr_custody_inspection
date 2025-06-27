# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CustodyImage(models.Model):
    _inherit = 'custody.image'

    inspection_id = fields.Many2one(
        'device.inspection',
        string='Inspection Record',
        ondelete='cascade',
        index=True,
        help='The inspection record this image belongs to'
    )

    # Override image_type to add inspection option
    image_type = fields.Selection([
        ('checkout', 'Checkout'),
        ('return', 'Return'),
        ('maintenance', 'Maintenance'),
        ('inspection', 'Inspection'),
        ('other', 'Other')
    ], 
        string='Image Type',
        required=True,
        default='other',
        index=True,
        help='Type of image - used for filtering and organizing'
    )

    @api.constrains('custody_id', 'inspection_id')
    def _check_record_reference(self):
        """Ensure image belongs to either custody or inspection, not both"""
        for record in self:
            if record.custody_id and record.inspection_id:
                raise ValidationError(_("Image cannot belong to both custody and inspection records."))

    @api.onchange('inspection_id')
    def _onchange_inspection_id(self):
        """Auto-set image type when inspection is selected"""
        if self.inspection_id:
            self.image_type = 'inspection'
            self.custody_id = False  # Clear custody if inspection is set

    @api.onchange('custody_id')
    def _onchange_custody_id(self):
        """Clear inspection when custody is selected"""
        if self.custody_id:
            self.inspection_id = False