# -*- coding: utf-8 -*-

from odoo import fields, models
from .postNL_requests import PostNLRequets
import logging
_logger = logging.getLogger(__name__)



class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(
        selection_add=[("post_nl", "PostNL")]
    )
    api_key

    
    def ship(self):
        data ={
            "Customer": {
                "Address": {
                    "AddressType": "02",
                    "City": "Hoofddorp",
                    "CompanyName": "PostNL",
                    "Countrycode": "NL",
                    "HouseNr": "42",
                    "Street": "Siriusdreef",
                    "Zipcode": "2132WT"
                },
                "CollectionLocation": "1234506",
                "ContactPerson": "Janssen",
                "CustomerCode": "DEVC",
                "CustomerNumber": "11223344",
                "Email": "email@company.com",
                "Name": "Janssen"
            },
            "Message": {
                "MessageID": "{{$guid}}",
                "MessageTimeStamp": "{{dateTime}}",
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
        request=PostNLRequets(data)
        _logger.info(" ship request response : %s" % (request))




        
