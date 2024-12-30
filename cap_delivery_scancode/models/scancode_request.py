# -*- coding: utf-8 -*-
import requests
import xml.etree.ElementTree as ET
from werkzeug.urls import url_join

from odoo.exceptions import UserError

# API_BASE_URL = "https://api.descartes.com/"  # Replace with actual base URL


class ScancodeRequest():

    def __init__(self, user_id, password, api_url, debug_logger):
        self.user_id = user_id
        self.password = password
        self.api_url = api_url
        self.debug_logger = debug_logger

    def _make_api_request(self, endpoint, request_type='post', data=None):
        """Make an API call and return response."""
        access_url = url_join(self.api_url, endpoint) #API_BASE_URL
        headers = {'Content-Type': 'text/xml; charset=utf-8'}
        try:
            self.debug_logger(f"URL: {access_url}\nType: {request_type}\nData: {data if data else 'None'}")
            if request_type == 'post':
                response = requests.post(access_url, data=data, headers=headers)
            else:
                raise ValueError("Unsupported request type")

            if response.status_code != 200:
                raise UserError(f"API request failed: {response.status_code} - {response.text}")
            return ET.fromstring(response.content)
        except Exception as e:
            raise UserError(f"Error in API request: {str(e)}")
