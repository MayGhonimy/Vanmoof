# -*- coding: utf-8 -*-

from odoo import _
from odoo.exceptions import ValidationError,UserError
import requests
import json



class PostNLRequets:
    def __init__(self, api_key=None):
        if api_key:
            self.api_key = api_key
        else:
            self.api_key='1'
        self.PostNL_URL = 'https://api-sandbox.postnl.nl/'

    def __str__(self):
        return f'PostNLRequets with key {self.api_key}'

    def ship(self,body):
        try:
            body = json.dumps(body)
        except Exception as e:
            raise  UserError( _('Data Error: [%s]'% (e) ))        
        hdr = {'content-type': 'application/json',
               'apikey': self.api_key}
        url = f'{self.PostNL_URL}v1/shipment'
        response = requests.post(url, data=body, headers=hdr)
        if response.status_code != 200:
            json_object_string=response.content.decode('utf-8')
            json_object = json.loads(str(json_object_string))
            raise ValidationError(_(f"Error<{response.status_code}>: {json_object['fault']['faultstring']}"))    

        return response