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

price_check_router = APIRouter()

#Odoo Class
class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"


    app: str = fields.Selection(selection_add=[("price_check", "Price Check")], ondelete={"price_check": "cascade"})


    def _get_fastapi_routers(self):
        if self.app == "price_check":
            return [price_check_router]
        return super()._get_fastapi_routers()

#Schemas
class ReturnValues(BaseModel):
    product_external_id : str = ""
    partner_external_id : str = ""
    price_list_currency : str = ""
    price_list_name : str = ""
    price_list_price : float = 0.0
    message : str = ""

class DataOutput(BaseModel):
    returnvalues: List[ReturnValues]

class DataInput(BaseModel):
    product_external_id : str
    partner_external_id : str
    currency : Optional[str] = None
    quantity : float

class DataPayload(BaseModel):
    company_id: Optional[str] = None
    data: List[DataInput]


def set_record_context(record_id, company_id, allowed_company_ids):
    '''
        Sets the context for a record, including company and language settings.

        Args:
            record_id: The record to set the context for.
            company_id: The company ID.
            allowed_company_ids: List of allowed company IDs.

        Returns:
            ctx_record: The record with the updated context.
    '''
    ctx_record = record_id.with_company(company_id)
    ctx_record = record_id.with_context({
            'allowed_company_ids':allowed_company_ids,
        })
    return ctx_record

#routers
@price_check_router.post("/price_checker")
def dynamic_upsert(payload: DataPayload, env: Environment = Depends(odoo_env)) -> DataOutput:
    '''
        FastAPI Route that will retrieve a pricelists price assuming that a product and partner XML id is provided along with an order quantity

        company_id is an optional param at the payload load level to check a pricelist for a specific SBC Company

        The data payload should also include a list of inputs at the top level

        Each input requires the following:
        - product_external_id
        - partner_external_id
        - quantity

        The return value will be a list of models with the following fields
        - product_external_id (from input)
        - partner_external_id (from input)
        - price_list_currency (from the partners pricelist, or default if the partner pricelist is not set)
        - price_list_name (from the partners pricelist, or default if the partner pricelist is not set)
        - price_list_price (calculated from the pricelist)
        - message (OK if no problem, otherwise the handled exception)
        
        
        
        Sample payload would be something like 
        {
            "company_id": "42",
            "data": [
                {
                    "product_external_id": "SYNTAX.PRODUCT_TEMPLATE_99",
                    "partner_external_id": "SYNTAX.RES_PARTNER_18",
                    "quantity": 99
                },
                {
                    ...
                }
            ]
        }

        Sample return would be something like:
        {
            "returnvalues":[
                {
                    "product_external_id": "SYNTAX.PRODUCT_TEMPLATE_99",
                    "partner_external_id": "SYNTAX.RES_PARTNER_18",
                    "price_list_currency": USD,
                    "price_list_name": "My Special Pricelist",
                    "price_list_price": 42.01,
                    "message": "OK"
                },
                {
                    ...
                }
            ]
        }

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
        instance_vals = ReturnValues(product_external_id=data.product_external_id, partner_external_id=data.partner_external_id, message="")
        try:
            if not data.quantity >= 0:
                instance_vals.message = f"Quantity should be >= 0\nReceived {data.quantity}"
                return_values.append(instance_vals)
                continue
            product_id = env.ref(data.product_external_id, raise_if_not_found=False)
            partner_id = env.ref(data.partner_external_id, raise_if_not_found=False)
            if not product_id or not partner_id:
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
            instance_vals.price_list_price = partner_id.property_product_pricelist._get_product_price(product=product_id, quantity=data.quantity, currency=currency_id)
            instance_vals.message = "OK"
        except Exception as e:
            instance_vals.message = f"EX Occured: {e}"
        return_values.append(instance_vals)
    output = DataOutput(returnvalues=return_values)
    return output