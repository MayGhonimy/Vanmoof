# -*- coding: utf-8 -*-

from odoo import fields, models,_
from .postNL_requests import PostNLRequets
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
import json
import time


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(
        selection_add=[("post_nl", "PostNL")]
    )
    api_key=fields.Char('PostNL Api Key')

    postnl_customer_code = fields.Char("Company Code")
    postnl_customer_number=fields.Char("Company Number")


    def _prepare_customer_data(self,picking):
        vals={}
        vals.update({"Address":
                {"AddressType": "02",
                 "City":picking.partner_id.city or ' ',
                 "CompanyName":picking.partner_id.name or ' ',
                 "Countrycode":picking.partner_id.country_id.code or ' ',
                 "HouseNr":picking.partner_id.street2 or ' ',
                 "Street":picking.partner_id.street or ' ',
                 "Zipcode": picking.partner_id.zip or ''

                },
                "CollectionLocation" : picking.company_id.zip or '',
                "ContactPerson": picking.company_id.name or '',
                "CustomerCode": picking.carrier_id.postnl_customer_code or '',
                "CustomerNumber":picking.carrier_id.postnl_customer_number or '' ,
                "Email":picking.company_id.email,
                "Name":picking.create_uid.name
                })
        return vals


    def _prepare_shipments_data(self,picking):
        
            


    def ship(self,pickings):
        
        current_date = time.strftime('%d-%m-%Y %H:%M:%S')
        data ={
            "Customer": self._prepare_customer(picking),
            "Message": {
                "MessageID": "01",
                "MessageTimeStamp": current_date,
                "Printertype": "GraphicFile|PDF"
            },
            "Shipments": [
                {
                    "Addresses": [
                        {
                            "AddressType": "01",
                            "City": "Shanghai",
                            "CompanyName": "PostNL",
                            "Countrycode": "CN",
                            "FirstName": "Peter",
                            "HouseNr": "137",
                            "Name": "de Ruiter",
                            "Street": "Nanjinglu",
                            "Zipcode": "310000"
                        }
                    ],
                    "Barcode": "{{s10barcode}}",
                    "Contacts": [
                        {
                            "ContactType": "01",
                            "Email": "receiver@email.com",
                            "SMSNr": "+31612345678"
                        }
                    ],
                    "Customs": {
                        "Content": [
                            {
                                "CountryOfOrigin": "NL",
                                "Description": "Powdered milk",
                                "HSTariffNr": "19019091",
                                "Quantity": "2",
                                "Value": "20.00",
                                "Weight": "4300"
                            }
                        ],
                        "Currency": "EUR",
                        "HandleAsNonDeliverable": "false",
                        "Invoice": "true",
                        "InvoiceNr": "22334455",
                        "ShipmentType": "Commercial Goods"
                    },
                    "Dimension": {
                        "Weight": "4300"
                    },
                    "ProductCodeDelivery": "4945"
                }
            ]
        }
        print(data)
        response=PostNLRequets(self.api_key).ship(data)
        
        print(response.content)
        _logger.info('PostNL Response : %s' % (response.content))
        print({response.content})
        




        
