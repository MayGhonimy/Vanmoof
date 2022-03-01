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
    postnl_default_product_code=fields.Selection([('3085', '3085: Dutch domestic products - Standard shipping - Guaranteed Morning delivery'),
                                                ('4945', '4945: Global shipping')
                                                #@ToDo add the rest of shipping types 
                                                ],default='3085',string="Default Product Code Delivery")
                        


    def get_product_code(self):
        """@TODO this function can be changed to check for sender 
        and reciver destion or add the product option to the SO or stock picking.
        Might need to add more paramters in the future """

        return self.postnl_default_product_code

    def _prepare_customer_data(self,picking):
        vals={}
        vals.update({"Address":
                {"AddressType": "02",
                 "City":picking.company_id.city or ' ',
                 "CompanyName":picking.company_id.name or ' ',
                 "Countrycode":picking.company_id.country_id.code or ' ',
                 "HouseNr":picking.company_id.street2 or ' ',
                 "Street":picking.company_id.street or ' ',
                 "Zipcode": picking.company_id.zip or ''

                },
                "CollectionLocation" : picking.company_id.zip or '',
                "ContactPerson": picking.company_id.name or '',
                "CustomerCode": picking.carrier_id.postnl_customer_code or '',
                "CustomerNumber":picking.carrier_id.postnl_customer_number or '' ,
                "Email":picking.company_id.email,
                "Name":picking.create_uid.name
                })
        return vals


    def _prepare_shipments_addresses_data(self,picking):
        vals={}
        vals.update(
                {"AddressType": "01",
                 "City":picking.partner_id.city or ' ',
                 "CompanyName":picking.partner_id.name or ' ',
                 "Countrycode":picking.partner_id.country_id.code or ' ',
                 "HouseNr":picking.partner_id.street2 or ' ',
                 "Street":picking.partner_id.street or ' ',
                 "Zipcode": picking.partner_id.zip or ''

                })
        return vals

    def _prepare_shipments_contacts_data(self,picking):
        vals={}
        vals.update(
                {"ContactType": "01",
                 "Email":picking.partner_id.email or ' ',
                 "SMSNr":picking.partner_id.phone or ' '
                })
        return vals

            


    def ship(self,pickings):
        
        current_date = time.strftime('%d-%m-%Y %H:%M:%S')
        data ={
            "Customer": self._prepare_customer_data(picking),
            "Message": {
                "MessageID": "01",
                "MessageTimeStamp": current_date,
                "Printertype": "GraphicFile|PDF"},
            "Shipments": [
                {
                    "Addresses" : [self._prepare_shipments_addresses_data(picking)],                    
                    "Contacts" : [self._prepare_shipments_contacts_data(picking)],
                    "Customs" : {
                        "Content": [{
                                "CountryOfOrigin": "NL",
                                "Description": "Powdered milk",
                                "HSTariffNr": "19019091",
                                "Quantity": "2",
                                "Value": "20.00",
                                "Weight": "4300"
                            }],
                        "Currency": "EUR",
                        "HandleAsNonDeliverable": "false",
                        "Invoice": "true",
                        "InvoiceNr": "22334455",
                        "ShipmentType": "Commercial Goods"
                    },
                    "Dimension": {
                        "Weight": "4300"
                    },
                    "ProductCodeDelivery": self.get_product_code()
                }
            ]
        }
        print(data)
        response=PostNLRequets(self.api_key).ship(data)
        
        print(response.content)
        _logger.info('PostNL Response : %s' % (response.content))
        print({response.content})
        




        
