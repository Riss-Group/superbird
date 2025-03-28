# Copyright 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# Copyright 2016-2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2024 Carolina Fernandez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Delivery costs in purchases",
    "version": "17.0.1.1.0",
    "development_status": "Production/Stable",
    "category": "Operations/Purchase",
    "website": "https://github.com/OCA/delivery-carrier",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["purchase", "stock_delivery"],
    "data": ["views/purchase_order_view.xml", "views/stock_picking_view.xml"],
}
