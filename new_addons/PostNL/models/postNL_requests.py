# -*- coding: utf-8 -*-

from odoo import _
from odoo.exceptions import ValidationError
import json
import requests


class PostNLRequets:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.PostNL_URL = "https://api-sandbox.postnl.nl/"

    def ship(self,body):   	

    	try:
    		body = json.dumps(data)
    	except Exception as e:
    		raise  ValidationError( _("Data Error: [%s]"% (e) ))
    	
        hdr = {"content-type": "application/json",
               "apikey": self.api_key}
        url = self.PostNL_URL
        response = requests.post(url, data=body, headers=hdr)
        
        response_body = request(method='POST', url=url, headers=headers,data=body)
        if response_body.status_code == 200:
        	return response_body