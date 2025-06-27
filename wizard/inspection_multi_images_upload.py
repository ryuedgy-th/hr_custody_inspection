# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import base64
import logging

_logger = logging.getLogger(__name__)

class InspectionMultiImagesUpload(models.TransientModel):
    _name = 'inspection.multi.images.upload'
    _description = 'Upload Multiple Inspection Images'

    inspection_id = fields.Many2one(
        'device.inspection',
        string='Inspection Record',
        required=True,
        ondelete='cascade'
    )
    
    image_type = fields.Selection([
        ('before', 'Before Inspection'),
        ('during', 'During Inspection'),
        ('after', 'After Inspection'),
        ('issue', 'Issues Found'),
        ('repair', 'Repair Documentation'),
        ('other', 'Other')
    ], 
        string='Image Type',
        required=True,
        default='during'
    )
    
    name = fields.Char(
        string='Title Base',
        help='Base title for the images (will be appended with a number)',
        default='Inspection Photo'
    )
    
    notes = fields.Text(
        string='Common Notes',
        help='Notes to apply to all uploaded images'
    )
    
    file_ids = fields.Many2many(
        'ir.attachment',
        string='Image Files',
        required=True,
        help='Select multiple image files to upload'
    )
    
    def action_upload_images(self):
        """Process selected files and create custody.image records"""
        self.ensure_one()
        
        CustodyImage = self.env['custody.image']
        images_created = 0
        errors = []
        
        _logger.info("Processing %d files for inspection %s", len(self.file_ids), self.inspection_id.name)
        
        for i, attachment in enumerate(self.file_ids):
            try:
                _logger.info("Processing file: %s, mimetype: %s", attachment.name, attachment.mimetype)
                
                # Check if file has image data
                if not attachment.datas:
                    _logger.warning("No data found for attachment: %s", attachment.name)
                    errors.append(f"No data found for {attachment.name}")
                    continue
                
                # Skip non-image files (but be more lenient)
                mimetype = attachment.mimetype or ''
                file_ext = attachment.name.lower().split('.')[-1] if '.' in attachment.name else ''
                is_image = (mimetype.startswith('image/') or 
                           file_ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'])
                
                if not is_image:
                    _logger.warning("Skipping non-image file: %s (mimetype: %s)", attachment.name, mimetype)
                    errors.append(f"Skipped non-image file: {attachment.name}")
                    continue
                
                # Create image title
                image_number = i + 1
                name = f"{self.name} {image_number}" if len(self.file_ids) > 1 else self.name
                
                # Map inspection image types to custody image types
                image_type_mapping = {
                    'before': 'inspection',
                    'during': 'inspection', 
                    'after': 'inspection',
                    'issue': 'inspection',
                    'repair': 'maintenance',
                    'other': 'inspection'
                }
                
                # Create custody image linked to inspection
                vals = {
                    'name': name,
                    'image': attachment.datas,
                    'inspection_id': self.inspection_id.id,
                    'image_type': image_type_mapping.get(self.image_type, 'inspection'),
                    'notes': self.notes or f"Inspection image ({self.image_type})",
                }
                
                _logger.info("Creating image with vals: %s", {k: v for k, v in vals.items() if k != 'image'})
                image = CustodyImage.create(vals)
                _logger.info("Successfully created image: %s (ID: %s)", image.name, image.id)
                images_created += 1
                
            except Exception as e:
                error_msg = f"Failed to process {attachment.name}: {str(e)}"
                _logger.error(error_msg)
                errors.append(error_msg)
        
        # Prepare result message
        if images_created > 0:
            message = _("%d images successfully uploaded") % images_created
            if errors:
                message += _("\n\nWarnings:\n%s") % '\n'.join(errors)
        else:
            message = _("No images were uploaded.")
            if errors:
                message += _("\n\nErrors:\n%s") % '\n'.join(errors)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Upload Complete'),
                'message': message,
                'sticky': bool(errors) or images_created == 0,
                'type': 'success' if images_created > 0 else 'warning',
                'next': {
                    'type': 'ir.actions.act_window_close'
                } if images_created > 0 else None
            }
        }
    
    def action_debug_files(self):
        """Debug method to check file information"""
        self.ensure_one()
        
        debug_info = []
        debug_info.append(f"Total files selected: {len(self.file_ids)}")
        debug_info.append(f"Inspection ID: {self.inspection_id.id}")
        
        for i, attachment in enumerate(self.file_ids):
            debug_info.append(f"\nFile {i+1}:")
            debug_info.append(f"  Name: {attachment.name}")
            debug_info.append(f"  Mimetype: {attachment.mimetype}")
            debug_info.append(f"  Has data: {bool(attachment.datas)}")
            debug_info.append(f"  Data size: {len(attachment.datas) if attachment.datas else 0} bytes")
        
        message = '\n'.join(debug_info)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Debug Information'),
                'message': message,
                'sticky': True,
                'type': 'info'
            }
        }