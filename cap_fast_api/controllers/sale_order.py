from typing import Annotated, Union, List, Dict, Optional
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
import logging

from odoo import fields, models, _
from odoo.api import Environment
from odoo.exceptions import UserError
from odoo.addons.fastapi.dependencies import odoo_env

_logger = logging.getLogger()

sale_order_router = APIRouter()

#Odoo Class
class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"


    app: str = fields.Selection(selection_add=[("sale_order", "Sale Order Router")], ondelete={"sale_order": "cascade"})


    def _get_fastapi_routers(self):
        if self.app == "sale_order":
            return [sale_order_router]
        return super()._get_fastapi_routers()

#Schemas
class ReturnValuesSO(BaseModel):
    sale_order_id : str = ""
    sale_order_name : str = ""
    message : str = ""

class DataPromoSO(BaseModel):
    promoname : Optional[str] = None
    discount : Optional[str] = None

class DataOrderDetailSO(BaseModel):
    itemno : str = None
    qty : float = 0.0
    prix : float = 0.0

class DataPayloadSO(BaseModel):
    companycode: str = None
    ponumber: Optional[str] = None
    custno: str = None
    discount: Optional[str] = None
    freeship: Optional[str] = None
    holdorder: Optional[str] = None
    onetimeship: Optional[str] = None
    promo: Optional[List[DataPromoSO]] = None
    orderdetail: List[DataOrderDetailSO] = None

#Helpers
def get_res_partner(env: Environment, custno=False):
    '''
        TODO DOCS
    '''
    if not custno:
        return False
    partner_id = env['res.partner'].search([('ref','=',custno)])
    return partner_id

def get_product(env: Environment, itemnno=False):
    '''
        TODO DOCS
    '''
    if not itemnno:
        return False
    product_id = env['product.product'].search([('name','=',itemnno)])
    return product_id

def get_company(env: Environment, companycode=False):
    '''
        TODO DOCS
    '''
    if not companycode:
        return False
    company_id = env['fastapi.company.map'].sudo().search([('name','=',companycode)],limit=1).company_id
    return company_id

def get_so_line_vals(product_id=False, qty=0, price=0, discount=0):
    '''
        TODO DOCS
    '''
    return (0,0,{
        'product_id' : product_id.id,
        'price_unit' : price,
        'product_uom_qty': qty,
        'discount': discount
    })

#routers
@sale_order_router.post("/sale_order")
def sale_order_create(payload: DataPayloadSO, env: Environment = Depends(odoo_env)) -> ReturnValuesSO:
    '''
        TODO DOCS
    '''
    return_values = ReturnValuesSO()
    #Handle company context
    if not payload.companycode:
        return_values.message = "The param 'companycode' was not provided and is required"
        return return_values
    company_id = get_company(env=env, companycode=payload.companycode)
    if not company_id:
        return_values.message = f"Could not find a matching Odoo company_id that matches the input code of [{payload.companycode}]"
        return return_values
    allowed_company_ids = env.user.company_ids.ids
    context = dict(env.context) 
    context.update({'allowed_company_ids': company_id.ids + [x for x in allowed_company_ids if x not in company_id.ids]})  
    env = env(context=context)
    #Handle Partner Lookup
    if not payload.custno:
        return_values.message = "The param 'custno' was not provided and is required"
        return return_values
    partner_id = get_res_partner(env=env, custno=payload.custno)
    if not partner_id:
        return_values.message = f"Could not find a matching Odoo partner that matches the custno provided of [{payload.custno}]"
        return return_values        
    # Determine Discount Percent
    discount = 0
    for promo in payload.promo:
        try:
            discount = float(promo.discount)
        except (ValueError, TypeError):
            continue
    #Process SO Header
    sale_order_vals = {
        'partner_id': partner_id.id,
        'client_order_ref' : payload.ponumber,
        'company_id': company_id.id,
    }
    #Process SO Lines
    order_line_vals = []
    for line in payload.orderdetail:
        product_id = get_product(env=env, itemnno=line.itemno)
        if not product_id:
            return_values.message = f"Could not find a matching Odoo product that matches the sku provided of [{line.itemno}]"
            return return_values   
        order_line_vals.append(get_so_line_vals(product_id=product_id, qty=line.qty, price=line.prix, discount=discount))
    sale_order_vals.update({'order_line': order_line_vals})
    order_id = env['sale.order'].create(sale_order_vals)
    #Process Free SHIP
    if str(payload.freeship) == 'Y' or str(payload.freeship) == 'y':
        carrier_id = env.ref('cap_fast_api.free_shipping', raise_if_not_found=False)
        if not carrier_id:
            return_values.message = f"The default free shipping method could not be located. Please contact the system adminstrator for support in resolving this issue"
        order_id.set_delivery_line(carrier_id, 0)
    output = ReturnValuesSO()
    output.sale_order_id = order_id.id
    output.sale_order_name = order_id.name
    output.message = "OK"
    return output