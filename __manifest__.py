# -*- coding: utf-8 -*-
{
    'name': 'HR Custody Device Inspection',
    'version': '18.0.1.0.0',
    'summary': 'Device inspection system for HR custody management',
    'description': """
Device Inspection Extension for HR Custody
=========================================

This module extends the HR Custody system with comprehensive device inspection capabilities:

Key Features:
- Create custom inspection types (End of Term, Renewal, Return, etc.)
- Detailed checklist-based inspections with scoring
- Photo documentation during inspections 
- Approval workflow (Draft → In Progress → Completed → Approved/Rejected)
- Integration with property management
- Pass/fail tracking with percentage calculations
- Inspector assignment and tracking

Perfect for international schools and organizations that need to track device 
condition during term-end checks, renewals, and returns.

Technical Features:
- Seamless integration with hr_custody module
- Extends custody.property with inspection functionality  
- Advanced view decorations and UI/UX
- Comprehensive security model
- Multi-language support ready
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'category': 'Human Resources',
    'depends': ['hr_custody', 'maintenance'],
    'data': [
        # Security files first
        'security/inspection_security.xml',
        'security/ir.model.access.csv',
        # Data files
        'data/inspection_sequence_data.xml',
        'data/inspection_type_data.xml',
        # Main views
        'views/device_inspection_views.xml',
        'views/custody_property_inspection_views.xml',
        'views/custody_image_inspection_views.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,  # This is an extension, not a standalone app
}