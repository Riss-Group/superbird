# -*- coding: utf-8 -*-
{
    'name': 'CAP Service',
    'category': 'Service',
    'summary': "CAP Service",
    'version': '1.4',
    'author': 'Captivea software Consulting, Bassim Elsamaloty',
    'website': 'https://www.captivea.com/',
    'license': 'OPL-1',
    'description': """
        Service for superbird.
        Integrates accounting, sales, fleet, purchase, inventory, rental, project into a custom service order data structure
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
        'sale_renting',
        'sale_renting_sign',
        'project_forecast',
        'industry_fsm_sale',
        'timesheet_grid'],
    'data': [
        'data/sequence.xml',
        'data/project_data.xml',
        'security/security_data.xml',
        'security/ir.model.access.csv',
        'report/report_invoice.xml',
        'report/sale_report_views.xml',
        'views/account_move.xml',
        'views/fleet_vehicle_model_brand.xml',
        'views/fleet_vehicle_model.xml',
        'views/fleet_vehicle.xml',
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
        'views/stock_move.xml',
        'wizard/fleet_acknowledge.xml',
        'wizard/service_ccc_edit.xml',
        'wizard/service_create_backorder.xml',
        'wizard/service_create_invoice.xml',
        'wizard/service_line_view_product.xml',
        'wizard/service_rental_order.xml',
        'wizard/service_template_select.xml',
        #Intentionally last to prevent dependency issues
        'views/_menus_actions.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}