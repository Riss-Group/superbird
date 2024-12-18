# -*- coding: utf-8 -*-
{
    'name': 'CAP Service',
    'category': 'Service',
    'summary': "CAP Service",
    'version': '1.2',
    'author': 'Captivea software Consulting, Bassim Elsamaloty',
    'website': 'https://www.captivea.com/',
    'license': 'OPL-1',
    'description': """
        TBD
        """,
    'depends': [
        'account', 
        'sale', 
        'stock', 
        'fleet', 
        'purchase',
        'product', 
        'project',
        'quality_control' ,
        'sale_planning',
        'sale_renting',
        'sale_renting_sign',
        'project_forecast',
        'timesheet_grid'],
    'data': [
        'data/sequence.xml',
        'report/sale_report_views.xml',
        'security/ir.model.access.csv',
        'views/_menus_actions.xml',
        'views/account_move.xml',
        'views/fleet_vehicle_model_brand.xml',
        'views/fleet_vehicle_model.xml',
        'views/fleet_vehicle.xml',
        'views/planning_slot.xml',
        'views/product_attribute.xml',
        'views/product_template.xml',
        'views/product_product.xml',
        'views/project_project.xml',
        'views/project_task.xml',
        'views/purchase_order.xml',
        'views/quality_point.xml',
        'views/res_company.xml',
        'views/sale_order.xml',
        'views/service_order_worksheets.xml',
        'views/service_order.xml',
        'views/service_template.xml',
        'views/stock_picking.xml',
        'wizard/fleet_acknowledge.xml',
        'wizard/service_ccc_edit.xml',
        'wizard/service_line_view_product.xml',
        'wizard/service_rental_order.xml',
        'wizard/service_template_select.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}