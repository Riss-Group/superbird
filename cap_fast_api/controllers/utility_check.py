from typing import Annotated, Union, List, Dict, Optional
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from odoo import fields, models, _
from odoo.api import Environment
from odoo.exceptions import UserError
from odoo.addons.fastapi.dependencies import odoo_env

_logger = logging.getLogger()

inventory_router = APIRouter()

#Odoo Class
class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"


    app: str = fields.Selection(selection_add=[("inventory_checker", "Inventory Router")], ondelete={"inventory_checker": "cascade"})


    def _get_fastapi_routers(self):
        if self.app == "inventory_checker":
            return [inventory_router]
        return super()._get_fastapi_routers()

#Schemas
#Price Checker
class PriceListEntryPC(BaseModel):
    price_list_price: float = 0.0
    min_qty: float = 0

class ReturnValuesPC(BaseModel):
    product_external_id: str = ""
    product_sku: str = ""
    partner_external_id: str = ""
    price_list_name: str = ""
    price_list_currency: str = ""
    prices: List[PriceListEntryPC] = [] 
    message: str = ""

class DataOutputPC(BaseModel):
    returnvalues: List[ReturnValuesPC] = []

class DataInputPC(BaseModel):
    product_external_id : Optional[str] = ""
    product_sku : Optional[str] = ""
    partner_external_id : str
    currency : Optional[str] = None

class DataPayloadPC(BaseModel):
    company_id: Optional[str] = None
    data: List[DataInputPC]

#Stock Checker
class WarehouseData(BaseModel):
    warehouse_id : int = None
    warehouse_name : str = ""
    on_hand : float = 0.0
    reserved : float = 0.0
    available : float = 0.0

class ReturnValuesWH(BaseModel):
    product_external_id : Optional[str] = ""
    product_sku: Optional[str] = ""
    message : str = ""
    warehouse_data : Optional[list[WarehouseData]] = None

class DataOutputWH(BaseModel):
    returnvalues: List[ReturnValuesWH]

class DataInputWH(BaseModel):
    product_external_id : Optional[str] = ""
    product_sku : Optional[str] = ""

class DataPayloadWH(BaseModel):
    warehouse_id: Optional[int] = None
    data: List[DataInputWH]

#helpers
def get_warehouse_external_id(env: Environment, warehouse_id=False):
    '''
        This helper method retrieves the external ID (XML ID) of a warehouse.

        If the `warehouse_id` is provided, it searches for the associated external ID in the `ir.model.data` table
        where the model is `stock.warehouse` and `res_id` corresponds to the provided warehouse ID.

        If no external ID is found, or if the warehouse_id is not provided, the method returns an empty string.

        Args:
            env (Environment): The Odoo environment object.
            warehouse_id (recordset, optional): The `stock.warehouse` record for which the external ID is needed. Default is `False`.

        Returns:
            str: The external ID of the warehouse, or an empty string if not found.

    '''
    if not warehouse_id:
        return ''
    xml_id = env['ir.model.data'].sudo().search([
        ('model','=','stock.warehouse'),
        ('res_id','=',warehouse_id.id)
    ])
    return xml_id.complete_name if xml_id else ''

def get_product_external_id(env: Environment, product_id=False):
    '''
        This helper method retrieves the external ID (XML ID) of a product.

        If the `product_id` is provided, it searches for the associated external ID in the `ir.model.data` table
        where the model is `product.product` and `res_id` corresponds to the provided product ID.

        If no external ID is found, or if the product_id is not provided, the method returns an empty string.

        Args:
            env (Environment): The Odoo environment object.
            product_id (recordset, optional): The `product.product` record for which the external ID is needed. Default is `False`.

        Returns:
            str: The external ID of the product, or an empty string if not found.
    '''
    if not product_id:
        return ''
    xml_id = env['ir.model.data'].sudo().search([
        ('model','=','product.product'),
        ('res_id','=',product_id.id)
    ])
    return xml_id.complete_name if xml_id else ''

#routers
@inventory_router.post("/price_checker")
def price_checker(payload: DataPayloadPC, env: Environment = Depends(odoo_env)) -> DataOutputPC:
    '''
        FastAPI Route that retrieves pricelist prices based on product and partner details provided in the payload.
        company_id is an optional param at the payload load level to check a pricelist for a specific SBC Company
        The data payload should also include a list of inputs at the top level

        Payload expects:
        - `company_id` (optional): Filters the pricelist by a specific SBC Company, if provided.
        - `data`: A list of inputs with each entry requiring:
            - `product_external_id` or `product_sku` (at least one is required)
            - `partner_external_id`
            - `quantity` (used for price calculation)

        Each input retrieves:
        - `product_external_id` (from input, if provided)
        - `product_sku` (from input, if provided)
        - `partner_external_id` (from input)
        - `price_list_currency` (derived from the partner's pricelist, or defaults if unset)
        - `price_list_name` (derived from the partner's pricelist, or defaults if unset)
        - `prices` list of objects (calculated from the applicable pricelist)
        - `message` ("OK" for success, otherwise provides handled exception details)
              
        Sample Payload:
        ```
        {
            "company_id": "42",
            "data": [
                {
                    "product_external_id": "SYNTAX.PRODUCT_TEMPLATE_99",
                    "product_sku": "Odoo product_id.name value"
                    "partner_external_id": "SYNTAX.RES_PARTNER_18",
                    "quantity": 99
                },
                ...
            ]
        }
        ```

        Sample Response:
        ```
        {
            "returnvalues":[
                {
                    "product_external_id": "SYNTAX.PRODUCT_TEMPLATE_99",
                    "product_sku": "Odoo product_id.name value",
                    "partner_external_id": "SYNTAX.RES_PARTNER_18",
                    "price_list_currency": "USD",
                    "price_list_name": "My Special Pricelist",
                    "prices": [
                        {"price_list_price": 42.01, "min_qty": 1}
                    ],
                    "message": "OK"
                },
                ...
            ]
        }
        ```

        Record Errors are returned per record level
        Other errors would be returned from FastAPI as {"detail":"I am Exception Text"}
    '''
    return_values = []
    allowed_company_ids = env.user.company_ids.ids
    company_id = env.company
    if payload.company_id:
        company_id = env['res.company'].search([('id','=',payload.company_id)])
        if not company_id or company_id.id not in env.user.company_ids.ids:
            raise HTTPException(status_code=400, detail="Company ID could not be found or the user does not have access to it")
    context = dict(env.context) 
    context.update({'allowed_company_ids': company_id.ids + [x for x in allowed_company_ids if x not in company_id.ids]})  
    env = env(context=context)  
    for data in payload.data:
        instance_vals = ReturnValuesPC()
        product_id = None
        try:
            if data.product_external_id:
                product_id = env.ref(data.product_external_id, raise_if_not_found=False)
            elif data.product_sku:
                product_id = env['product.product'].search([('name', '=', data.product_sku)], limit=1)
            if not product_id:
                instance_vals.message = f"Product not found. Checked External ID: {data.product_external_id}, SKU: {data.product_sku}"
                return_values.append(instance_vals)
                continue
            partner_id = env.ref(data.partner_external_id, raise_if_not_found=False)
            if not partner_id:
                instance_vals.message = f"Product or Partner not found. Vals found: Product {product_id} Partner {partner_id}"
                return_values.append(instance_vals)
                continue
            pricelist_id = partner_id.property_product_pricelist
            currency_id = pricelist_id.currency_id
            if data.currency:
                currency_id = env['res.currency'].search([
                    ('name','=',data.currency),
                    ('active','=', True)
                ])
                if not currency_id:
                    instance_vals.message = f"Specific currency passed but not found. Consider not passing this param. Currency passed: {data.currency}"
                    return_values.append(instance_vals)
                    continue
            instance_vals.price_list_name = str(pricelist_id.name)
            instance_vals.price_list_currency = str(currency_id.name)
            pricelist_item_ids = pricelist_id._get_applicable_rules_api(product_id)
            pricelist_entries = []
            if pricelist_item_ids:
                for pricelist_item_id in pricelist_item_ids:
                    price = pricelist_item_id._compute_price(
                        product=product_id, 
                        quantity=pricelist_item_id.min_quantity,
                        uom=product_id.uom_id,
                        date=datetime.now())
                    pricelist_entries.append(PriceListEntryPC(price_list_price=price, min_qty=pricelist_item_id.min_quantity))
            else:
                price = product_id.lst_price if product_id._name == 'product.product' else product_id.list_price
                pricelist_entries.append(PriceListEntryPC(price_list_price=product_id.list_price, min_qty=0))
            instance_vals.prices = pricelist_entries
            instance_vals.message = "OK"
        except Exception as e:
            instance_vals.message = f"EX Occured: {e}"
        return_values.append(instance_vals)
    output = DataOutputPC(returnvalues=return_values)
    return output

@inventory_router.post("/stock_checker")
def stock_checker(payload: DataPayloadWH, env: Environment = Depends(odoo_env)) -> DataOutputWH:
    '''
        FastAPI Route that retrieves inventory data for a product, assuming that a product's XML ID or SKU is provided.

        The payload may also include a specific warehouse's ID to filter the results by that warehouse. If no
        warehouse is provided, inventory data for all available warehouses will be returned.

        The `data` payload should include a list of inputs with the following fields:
        - `product_external_id`: XML ID of the product (prioritized if set)
        - `product_sku`: SKU of the product

        **Return Values**:
        For each product, the return value contains:
        - `product_external_id`: From input or computed if not provided
        - `product_sku`: From input or computed if not provided
        - `warehouse_data`: List of warehouse records with `on_hand`, `reserved`, and `available` quantities
        - `message`: "OK" if no issues; an error message if any issues occurred


        **Error Handling**:
        - Record-level errors are included in each individual entry within `returnvalues`.
        - General errors (e.g., authorization) are returned as `{"detail": "Error message"}`.

        **Sample Payload**:
        ```
        {
            "warehouse_id": 42,
            "data": [
                {
                    "product_external_id": "SYNTAX.PRODUCT_TEMPLATE_99",
                    "product_sku": "PROD99"
                },
                ...
            ]
        }
        ```

        **Sample Response**:
        ```
        {
            "returnvalues": [
                {
                    "product_external_id": "SYNTAX.PRODUCT_TEMPLATE_99",
                    "product_sku": "PROD99",
                    "warehouse_data": [
                        {
                            "warehouse_id": 42,
                            "warehouse_name": "Main Warehouse",
                            "on_hand": 100,
                            "reserved": 20,
                            "available": 80
                        }
                    ],
                    "message": "OK"
                },
                ...
            ]
        }
        ```
    '''
    return_values = []
    allowed_company_ids = env.user.company_ids.ids
    company_id = env.company
    context = dict(env.context) 
    context.update({'allowed_company_ids': company_id.ids + [x for x in allowed_company_ids if x not in company_id.ids]})  
    env = env(context=context)
    warehouse_ids = env['stock.warehouse'].search([])
    for data in payload.data:
        instance_vals = ReturnValuesWH(product_external_id=data.product_external_id, message="")
        try:
            product_id = env['product.product']
            if data.product_external_id:
                product_id = env.ref(data.product_external_id, raise_if_not_found=False)
            elif data.product_sku:
                product_id = product_id.search([('name','=',data.product_sku)],limit=1)
            if not product_id:
                instance_vals.message = f"Product external id or sku was not found."
                return_values.append(instance_vals)
                continue
            whse_data_list = []
            if payload.warehouse_id:
                warehouse_ids = warehouse_ids.filtered(lambda x: x.id == payload.warehouse_id)
                if not warehouse_ids:
                    raise UserError(f"Warehouse with id [{payload.warehouse_id}] was not found")
            for warehouse_id in warehouse_ids:
                quant_ids = env['stock.quant'].search([
                    ('location_id.warehouse_id','=',warehouse_id.id),
                    ('product_id','=',product_id.id)
                ])
                whse_data = WarehouseData()
                whse_data.warehouse_id = warehouse_id.id
                whse_data.warehouse_name = warehouse_id.name
                whse_data.available = sum(quant_ids.mapped('available_quantity'))
                whse_data.reserved = sum(quant_ids.mapped('reserved_quantity'))
                whse_data.on_hand = sum(quant_ids.mapped('quantity'))
                whse_data_list.append(whse_data)
            instance_vals.warehouse_data = whse_data_list
            instance_vals.product_external_id = data.product_external_id or get_product_external_id(env=env, product_id=product_id)
            instance_vals.product_sku = data.product_sku or product_id.name
            instance_vals.message = "OK"
        except Exception as e:
            instance_vals.message = f"EX Occured: {e}"
        return_values.append(instance_vals)
    output = DataOutputWH(returnvalues=return_values)
    return output