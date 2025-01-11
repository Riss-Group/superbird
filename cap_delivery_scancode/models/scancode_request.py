# -*- coding: utf-8 -*-
import requests
import urllib.parse
import xml.etree.ElementTree as ET
from werkzeug.urls import url_join
from lxml import etree

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
        print(endpoint, request_type, data)
        try:
            # self.debug_logger(f"URL: {access_url}\nType: {request_type}\nData: {data if data else 'None'}")
            self.debug_logger("%s\n%s\n%s" % (access_url, request_type, data if data else None),
                              'scancode_request_%s' % endpoint)
            if request_type == 'post':
                response = requests.post(access_url, data=data, headers=headers)
            else:
                raise ValueError("Unsupported request type")

            if response.status_code != 200:
                raise UserError(f"API request failed: {response.status_code} - {response.text}")
            # Step 1: Decode the URL-encoded XML string
            decoded_xml = urllib.parse.unquote(response.content).strip()
            decoded_xml = decoded_xml.replace('+', ' ')
            print(decoded_xml)

            root = ET.fromstring(decoded_xml)
            return root
        except Exception as e:
            raise UserError(f"Error in API request: {str(e)}")
