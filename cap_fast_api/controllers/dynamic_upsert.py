from typing import Annotated, Union, List, Dict, Optional
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
import pprint
import logging

from odoo import fields, models, _
from odoo.api import Environment
from odoo.exceptions import UserError
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
    m2m_link: Optional[str] = 'link'
    fields: Optional[Dict[str, Union[str, int, float, bool]]] = Field(default_factory=dict)

class DataOutput(BaseModel):
    model: Union[str, bool]
    returnvalues: List[ReturnValues]

class DataInput(BaseModel):
    external_id: str
    fields: Dict[str, Union[str, int, float, bool, List[RelatedOne2ManyRecord], dict]] = Field(default_factory=dict)

class DataPayload(BaseModel):
    model: str
    lang: Optional[str] = None
    company_id: Optional[str] = None
    data: List[DataInput]

#Helper Methods
def create_xml_id(env: Environment, external_id: str, model: str, res_id: int):
    '''
        Creates or retrieves an existing XML ID for a given record.

        Args:
            env (Environment): The Odoo environment.
            external_id (str): The external ID to create or retrieve.
            model (str): The model name of the record.
            res_id (int): The ID of the record.

        Returns:
            existing_record: The created or existing record.
    '''
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

def set_record_context(record_id, lang, company_id, allowed_company_ids):
    '''
        Sets the context for a record, including company and language settings.

        Args:
            record_id: The record to set the context for.
            lang (str): The language code.
            company_id: The company ID.
            allowed_company_ids: List of allowed company IDs.

        Returns:
            ctx_record: The record with the updated context.
    '''
    allowed_company_ids = company_id.ids + [x for x in allowed_company_ids if x not in company_id.ids]
    ctx_record = record_id.with_context({
            'allowed_company_ids':allowed_company_ids,
            'lang':lang
        })
    return ctx_record

def convert_json_strings(fields):
    '''
        Converts JSON strings in the fields dictionary to Python objects.

        Args:
            fields (dict): The fields dictionary with potential JSON strings.

        Returns:
            dict: The fields dictionary with JSON strings converted to Python objects.
    '''
    for key, value in fields.items():
        if isinstance(value, str):
            try:
                fields[key] = value
            except json.JSONDecodeError:
                pass
        elif isinstance(value, dict):
            fields[key] = convert_json_strings(value)
        elif isinstance(value, list):
            fields[key] = [convert_json_strings(item) if isinstance(item, dict) else item for item in value]
    return fields

def _is_field_editable(field):
    if field.readonly:
        return False
    if not field.store and field.compute and not field.inverse:
        return False
    return True

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
            If the Odoo field is a m2m, iterate over the list of related records.
            For each related record:
                If it has an external ID, resolve it to the actual record ID.
                    If the related record exists, update its fields if any.
                    If the related record does not exist, create a new record and process its fields.
                    If unlink is passed into the schema (m2m_link: "unlink") then remove that external IDs relation to this one
                    If link is passed and fields are not then only create the link between record and self
                Add the processed record to vals_dict with the appropriate operation code.

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
            raise UserError(f"Field {field_name} does not exist on model {model}")
        if not _is_field_editable(field):
            field_properties = {
                "type": field.type,
                "readonly": field.readonly,
                "compute": bool(field.compute),
                "inverse": bool(field.inverse),
                "related": field.related,
                "store": field.store,
                "string": field.string,
            }
            raise UserError(f"Field {field_name} is not considered editable. Field Properties: {field_properties}")
        if field.type == 'many2one':
            if isinstance(field_value, str) and '.' in field_value:
                related_record = env.ref(field_value, raise_if_not_found=False)
                if not related_record:
                    raise UserError(f"Invalid external ID {field_value} for field {field_name}")
                vals_dict[field_name] = related_record.id
            else:
                vals_dict[field_name] = field_value
        elif field.type == 'one2many':
            if not isinstance(field_value, list):
                raise UserError(f"Field {field_name} must be a list of dictionaries")
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
        elif field.type == 'many2many':
            if not isinstance(field_value, list):
                raise UserError(f"Field {field_name} must be a list of IDs or external IDs")
            m2m_vals = []
            for related_data in field_value:
                if isinstance(related_data, dict):
                    related_data = RelatedOne2ManyRecord(**related_data)
                related_fields = False
                if related_data.fields:
                    related_fields = process_fields(env, field.comodel_name, related_data.fields)
                if related_data.external_id:
                    related_record = env.ref(related_data.external_id, raise_if_not_found=False)
                    if related_record and related_fields:
                        m2m_vals.append((1, related_record.id, related_fields))
                    elif related_record and related_data.m2m_link == 'unlink':
                        m2m_vals.append((3, related_record.id, 0))
                    elif related_record and (not related_fields or related_data.m2m_link == 'link'):
                        m2m_vals.append((4, related_record.id, 0))
                    elif not related_record and related_fields:
                        related_fields['external_id_to_create'] = related_data.external_id
                        m2m_vals.append((0, 0, related_fields))
                else:
                    if related_fields:
                        m2m_vals.append((0,0, related_fields))
                    else:
                        raise UserError(f"Field {field_name} was malformed by missing external ID and fields to create Payload")
            if m2m_vals:
                vals_dict[field_name] = m2m_vals
        else:
            if field.type in ['char', 'selection', 'text']:
                vals_dict[field_name] = str(field_value)
            else:
                vals_dict[field_name] = field_value
    return vals_dict

#routers
@dynamic_upsert_router.post("/dynamic/xml_id")
def dynamic_upsert(payload: DataPayload, env: Environment = Depends(odoo_env)) -> DataOutput:
    '''
        FastAPI Route that will dynamically UPSERT any data passed via XML ID

        - `lang` and `company_id` can be passed in for context specific results (optional)
        - m2o/o2m/m2m fields can be processed as well. 
        - m2o requires XML ID to exist or will return a not found error
        - o2m will create the XML ID if it does not exist
        - m2m also requires the XML ID 
            - It does not require a 'fields' payload since it could be linked or unlinked. 
            - To specify a record to be unlinked an optional 'm2m_link' parameter can be passed that accepts values of 'link' (default) or 'unlink'
        
        Sample payload:
        ```
        {
        "model": "res.partner",
        "company_id": "42",
        "lang": "fr_CA",
        "data": [
            {
            "external_id": "SYNTAX_TEST.Partner123",
            "fields": {
                "company_id": 42,
                "name": "test12345",
                "category_id": [
                {
                    "external_id": "SYNTAX.res_partner_category_1",
                    "fields": {
                    "name": "Category 1",
                    "color": 5
                    }
                },
                {
                    "external_id": "SYNTAX.res_partner_category_2",
                    "m2m_link": "link"
                }
                ]
            }
            }
        ]
        }
        ```

        Sample Response:
        ```
        {
            "model":"res.partner",
            "returnvalues":[
                {
                    "external_id":"SYNTAX_TEST.Partner123",
                    "message":"OK"
                }
            ]
        }
        ```

        Record Errors are returned per record level
        Other errors would be returned from FastAPI as {"detail":"I am Exception Text"}
    '''
    return_values = []
    allowed_company_ids = env.user.company_ids.ids
    company_id = env.company
    odoo_lang= env.lang
    odoo_model = env['ir.model'].sudo().search([('model','=',payload.model)])
    if not odoo_model:
        raise HTTPException(status_code=400, detail="Invalid model passed")
    if payload.lang:
        odoo_lang = env['res.lang'].search([
            ('active','=',True), 
            ('code','=',payload.lang)
        ]).code
        if not odoo_lang:
            raise HTTPException(status_code=400, detail="Language code passed does not match an active Odoo Language")
    if payload.company_id:
        company_id = env['res.company'].search([('id','=',payload.company_id)])
        if not company_id or company_id.id not in env.user.company_ids.ids:
            raise HTTPException(status_code=400, detail="Company ID could not be found or the user does not have access to it")
    for data in payload.data:
        instance_vals = ReturnValues(external_id=data.external_id, message="")
        fields_with_json = convert_json_strings(data.fields)
        resolved_fields = False
        try:
            resolved_fields = process_fields(env, payload.model, fields_with_json)
        except Exception as e:
            resolved_fields = False
            instance_vals.message = f"PROCESS FIELDS EX: {str(e)}"
        record_id = env.ref(data.external_id, raise_if_not_found=False)
        if record_id and resolved_fields:
            try:
                record_id = set_record_context(record_id=record_id, lang=odoo_lang, company_id=company_id, allowed_company_ids=allowed_company_ids)
                if record_id.write(resolved_fields):
                    instance_vals.message = "OK"
                else:
                    instance_vals.message = "Unknown Error Occured while writing data"
            except Exception as e:
                instance_vals.message = f"WRITE EX: {e}"
        elif resolved_fields:
            try:
                record_id = env[payload.model]
                record_id = set_record_context(record_id=record_id, lang=odoo_lang, company_id=company_id, allowed_company_ids=allowed_company_ids)
                record_id = record_id.create(resolved_fields)
                xml_id = create_xml_id(env, data.external_id, payload.model, record_id.id)
                if record_id and xml_id:
                    instance_vals.message = "OK"
                else:
                    instance_vals.message = "Unknown Error Occured while creating data"
            except Exception as e:
                instance_vals.message = f"CREATE EX: {e}"
        return_values.append(instance_vals)
    output = DataOutput(model=payload.model, returnvalues=return_values)
    return output