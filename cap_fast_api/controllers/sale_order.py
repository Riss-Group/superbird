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
    custno: Optional[str] = None
    partner_id: Optional[int] = None
    discount: Optional[str] = None
    freeship: Optional[str] = None
    holdorder: Optional[str] = None
    onetimeship: Optional[str] = None
    promo: Optional[List[DataPromoSO]] = None
    orderdetail: List[DataOrderDetailSO] = None

#Helpers
def get_res_partner(env: Environment, custno=False, db_id=False):
    '''
        This helper method retrieves a partner record from the Odoo database based on the given customer reference number (`custno`) or database ID (`db_id`).

        If `db_id` is provided, the method searches for a partner whose ID matches the given value.
        If `custno` is provided and `db_id` is not, the method searches for a partner whose reference matches the given value in the `res.partner` model.
        If neither `custno` nor `db_id` are provided, the method returns an empty recordset.

        Args:
            env (Environment): The Odoo environment object.
            custno (str, optional): The customer reference number. Default is `False`.
            db_id (int, optional): The database ID of the partner. Default is `False`.

        Returns:
            recordset: The `res.partner` record that matches the given `custno` or `db_id`, or an empty recordset if not found.
    '''
    partner_id = env['res.partner']
    if not custno and not db_id:
        pass
    elif db_id:
        partner_id = env['res.partner'].search([('id','=',db_id)])
    elif custno:
        partner_id = env['res.partner'].search([('ref','=',custno)])
    return partner_id

def get_product(env: Environment, itemnno=False):
    '''
        This helper method retrieves a product record from the Odoo database based on the given item number (`itemnno`).

        If `itemnno` is provided, the method searches for a product whose name matches the given value in the `product.product` model.
        If no matching product is found or `itemnno` is not provided, the method returns `False`.

        Args:
            env (Environment): The Odoo environment object.
            itemnno (str, optional): The item number of the product. Default is `False`.

        Returns:
            recordset: The `product.product` record that matches the given `itemnno`, or `False` if not found.
    '''
    if not itemnno:
        return False
    product_id = env['product.product'].search([('name','=',itemnno)])
    return product_id

def get_company(env: Environment, companycode=False):
    '''
        This helper method retrieves a company record from the Odoo database based on the given company code (`companycode`).

        If `companycode` is provided, the method searches for a company mapping in the `fastapi.company.map` model and retrieves the corresponding company record.
        If no matching company is found or `companycode` is not provided, the method returns `False`.

        Args:
            env (Environment): The Odoo environment object.
            companycode (str, optional): The company code. Default is `False`.

        Returns:
            recordset: The `res.company` record that matches the given `companycode`, or `False` if not found.
    '''
    if not companycode:
        return False
    company_id = env['fastapi.company.map'].sudo().search([('name','=',companycode)],limit=1).company_id
    return company_id

def get_so_line_vals(product_id=False, qty=0, price=0, discount=0):
    '''
        This helper method creates a dictionary of values for a sale order line.

        The method takes in the product, quantity, price, and discount, and creates a dictionary containing these values,
        which can be used to create or update sale order lines in the `sale.order.line` model.

        Args:
            product_id (recordset, optional): The `product.product` record representing the product to be added to the sale order line. Default is `False`.
            qty (float, optional): The quantity of the product. Default is `0`.
            price (float, optional): The price per unit of the product. Default is `0`.
            discount (float, optional): The discount to be applied to the product. Default is `0`.

        Returns:
            tuple: A tuple with sale order line values, suitable for use in a one2many field.
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
        FastAPI Route that creates a sale order in Odoo based on the provided payload.

        The payload should include the company code, customer number, and order details.
        Additional parameters like discount, free shipping, and promotional details can also be provided.

        The method handles the following steps:
        - Look up the company by the provided `companycode`.
        - Look up the customer by the provided `partner_id` or `custno`. Partner ID is prioritized
        - Determine any applicable discount based on promotions.
        - Create a sale order header and order lines based on the provided product details.
        - If free shipping is indicated, apply the free shipping method to the sale order.

        Args:
            payload (DataPayloadSO): The sale order data payload.
            env (Environment): The Odoo environment object.

        Returns:
            ReturnValuesSO: The response containing sale order ID, sale order name, and a message indicating success or failure.

        Sample payload:
        {
            "companycode": "P",
            "ponumber": "PO123456",
            "partner_id": 42
            "custno": "CUST001",
            "discount": "5",
            "freeship": "Y",
            "holdorder": "N",
            "onetimeship": "N",
            "promo": [
                {
                    "promoname": "Promo1",
                    "discount": "10"
                }
            ],
            "orderdetail": [
                {
                    "itemno": "ITEM001",
                    "qty": 5,
                    "prix": 100.0
                },
                {
                    "itemno": "ITEM002",
                    "qty": 2,
                    "prix": 50.0
                }
            ]
        }

        Sample return:
        {
            "sale_order_id": "123",
            "sale_order_name": "SO001",
            "message": "OK"
        }
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
    if not payload.custno and not payload.partner_id:
        return_values.message = "The param 'custno' AND partner_id was not provided and at least one is required"
        return return_values
    partner_id = get_res_partner(env=env, custno=payload.custno, db_id=payload.partner_id)
    if not partner_id:
        return_values.message = f"Could not find a matching Odoo partner that matches the custno provided of [{payload.custno}] or partner_id of [{payload.partner_id}]"
        return return_values        
    # Determine Discount Percent
    discount = 0
    for promo in payload.promo or []:
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