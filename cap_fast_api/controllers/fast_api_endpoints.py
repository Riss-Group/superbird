from typing import Annotated, Union, List, Dict, Optional
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
import logging

from odoo import fields, models, _
from odoo.api import Environment
from odoo.addons.fastapi.dependencies import odoo_env

_logger = logging.getLogger()

dynamic_upsert_router = APIRouter()

#Odoo Class
class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"


    app: str = fields.Selection(selection_add=[("dynamic_upsert", "Dynamic Upsert")], ondelete={"dynamic_upsert": "cascade"})


    def _get_fastapi_routers(self):
        if self.app == "dynamic_upsert":
            return [dynamic_upsert_router]
        return super()._get_fastapi_routers()

#Schemas
class ReturnValues(BaseModel):
    external_id : str
    message : str

class RelatedOne2ManyRecord(BaseModel):
    external_id: str
    fields: Dict[str, Union[str, int, float, bool]] = Field(default_factory=dict)

class DataOutput(BaseModel):
    model: Union[str, bool]
    returnvalues: List[ReturnValues]

class DataInput(BaseModel):
    external_id: str
    fields: Dict[str, Union[str, int, float, bool, List[RelatedOne2ManyRecord], dict]] = Field(default_factory=dict)

class DataPayload(BaseModel):
    model: str
    lang: Optional[str] = None
    data: List[DataInput]

#Helper Methods
def create_xml_id(env: Environment, external_id: str, model: str, res_id: int):
    module = external_id.split('.')[0]
    name = external_id.split('.', 1)[1]
    existing_record = env['ir.model.data'].search([('module', '=', module), ('name', '=', name)])
    if not existing_record:
        existing_record = env['ir.model.data'].create({
            'module': module,
            'model': model,
            'name': name,
            'res_id': res_id
        })
    return existing_record

def convert_json_strings(fields):
    for key, value in fields.items():
        if isinstance(value, str):
            try:
                fields[key] = json.loads(value)
            except json.JSONDecodeError:
                pass
        elif isinstance(value, dict):
            fields[key] = convert_json_strings(value)
        elif isinstance(value, list):
            fields[key] = [convert_json_strings(item) if isinstance(item, dict) else item for item in value]
    return fields

def process_fields(env: Environment, model: str, fields: Dict[str, Union[str, int, float, bool, List[Dict]]]) -> Dict[str, Union[str, int, float, bool]]:
    '''
        Takes the fields passed in from the payload and converts them into a proper odoo vals dict for write/create
        
        Non-related Field:
            Copies the dict instance as is for vals_dict

        m2o:
            If the Odoo field is a m2o then we need to consider if the value passed in the field is an id or external_id
            If its an external ID then search ir.model.data for its external_id and update vals_dict with the appropriate record_id
            If its a normal ID copy it as is

        o2m:
            If the Odoo field is a o2m then we need to iterate over the list of related records
            For each related record:
                If it has an external ID, resolve it to the actual record ID and process its fields recursively
                If it doesn't have an external ID, create a new record and process its fields recursively
                Add the processed record to vals_dict with the appropriate operation code

        m2m:
            Not Implemented and throws user error
            If needed this should be resolved in a future update

        Non-stored field:
            Throws User Error and explains to user error that they cannot update non-stored fields

        params:
            fields: Dict List

        returns:
            vals_dict: Dict List
    '''
    vals_dict = {}
    odoo_model = env[model]
    for field_name, field_value in fields.items():
        field = odoo_model._fields.get(field_name)
        if field is None:
            raise HTTPException(status_code=400, detail=f"Field {field_name} does not exist on model {model}")        
        if not field.store:
            raise HTTPException(status_code=400, detail=f"Field {field_name} is not a stored field and cannot be updated")        
        if field.type == 'many2one':
            if isinstance(field_value, str) and '.' in field_value:
                related_record = env.ref(field_value, raise_if_not_found=False)
                if not related_record:
                    raise HTTPException(status_code=400, detail=f"Invalid external ID {field_value} for field {field_name}")
                vals_dict[field_name] = related_record.id
            else:
                vals_dict[field_name] = field_value
        elif field.type == 'one2many':
            if not isinstance(field_value, list):
                raise HTTPException(status_code=400, detail=f"Field {field_name} must be a list of dictionaries")
            o2m_vals = []
            for related_data in field_value:
                if isinstance(related_data, dict):
                    related_data = RelatedOne2ManyRecord(**related_data)
                related_fields = process_fields(env, field.comodel_name, related_data.fields)
                if related_data.external_id:
                    related_record = env.ref(related_data.external_id, raise_if_not_found=False)
                    if related_record:
                        o2m_vals.append((1, related_record.id, related_fields))
                    else:
                        related_fields['external_id_to_create'] = related_data.external_id
                        o2m_vals.append((0,0, related_fields))
                else:
                    o2m_vals.append((0, 0, related_fields))
            vals_dict[field_name] = o2m_vals
        elif field.type in ('many2many'):
            raise HTTPException(status_code=400, detail=f"Field {field_name} of type {field.type} is not implemented")
        else:
            vals_dict[field_name] = field_value
    return vals_dict

#routers
@dynamic_upsert_router.post("/dynamic/xml_id")
def dynamic_upsert(payload: DataPayload, env: Environment = Depends(odoo_env)) -> DataOutput:
    '''
        FastAPI Route that will dynamically UPSERT any data passed via XML ID
        m2o and o2m fields can be processed as well. 
        m2o requires XML ID to exist or will return a not found error for obvious reasons
        o2m will create the XML ID if it does not exist for obvious reasons
        
        Sample payload would be something like 
        {
            "model": "res.partner",
            "data": [
                {
                "external_id": "SYNTAX_TEST.Partner123",
                "fields": {
                    "name": "Test123",
                    "email": "Test123@gmail.com"
                }
            }]
        }

        Sample return would be something like:
        {
            "model":"res.partner",
            "returnvalues":[
                {
                    "external_id":"SYNTAX_TEST.Partner123",
                    "message":"OK"
                }
            ]
        }

        Record Errors are returned per record level
        Other errors would be returned from FastAPI as {"detail":"I am Exception Text"}
    '''
    return_values = []
    odoo_model = env['ir.model'].search([('model','=',payload.model)])
    if not odoo_model:
        raise HTTPException(status_code=400, detail="Invalid model passed")
    odoo_lang= env.lang
    if payload.lang:
        odoo_lang = env['res.lang'].search([
            ('active','=',True), 
            ('code','=',payload.lang)
        ]).code
        if not odoo_lang:
            raise HTTPException(status_code=400, detail="Language code passed does not match an active Odoo Language")
    for data in payload.data:
        fields_with_json = convert_json_strings(data.fields)
        resolved_fields = process_fields(env, payload.model, fields_with_json)
        record_id = env.ref(data.external_id, raise_if_not_found=False)
        instance_vals = ReturnValues(external_id=data.external_id, message="")
        if record_id:
            if record_id.with_context({'lang':odoo_lang}).write(resolved_fields):
                instance_vals.message = "OK"
            else:
                instance_vals.message = "Unknown Error Occured while writing data"
        else:
            record_id = env[payload.model].with_context({'lang':odoo_lang}).create(resolved_fields)
            xml_id = create_xml_id(env, data.external_id, payload.model, record_id.id)
            if record_id and xml_id:
                instance_vals.message = "OK"
            else:
                instance_vals.message = "Unknown Error Occured while creating data"
        return_values.append(instance_vals)
    output = DataOutput(model=payload.model, returnvalues=return_values)
    return output