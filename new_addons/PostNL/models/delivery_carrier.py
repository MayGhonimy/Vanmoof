# -*- coding:  utf-8 -*-

from odoo import fields,  models, api, _
from .postNL_requests import PostNLRequets
from odoo.exceptions import UserError
from odoo.exceptions import UserError
import json
import time
import logging
_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"
    delivery_type = fields.Selection(selection_add=[("post_nl",  "PostNL")])
    api_key = fields.Char('PostNL Api Key')
    postnl_customer_code = fields.Char("Company Code")
    postnl_customer_number = fields.Char("Company Number")
    postnl_default_product_code = fields.Selection([('3085',  '3085, Dutch domestic products - Standard shipping - Guaranteed Morning delivery'),
                                                    ('4945',  '4945: Global shipping')
                                                    # @ToDo add the rest of shipping types
                                                    ], default='3085', string="Default Product Code Delivery")
    postnl_gloable_license_nr = fields.Char("Global Shipping License")

    def get_product_code(self, picking):
        """@TODO this function can be changed to check for sender
        and reciver destion or add the product option to the SO or stock picking.
        Might need to add more paramters in the future """
        return picking.carrier_id.postnl_default_product_code

    def _prepare_shipments_addresses_data(self, picking):
        vals = {}
        vals.update({"AddressType":  "01",
                 "City": picking.partner_id.city or ' ',
                 "CompanyName": picking.partner_id.name or ' ',
                 "Countrycode": picking.partner_id.country_id.code or ' ',
                 "HouseNr": picking.partner_id.street2 or ' ',
                 "Street": picking.partner_id.street or ' ',
                 "Zipcode":  picking.partner_id.zip or ''})
        return vals

    def _prepare_shipments_contacts_data(self, picking):
        vals={}
        vals.update({"ContactType":  "01",
                 "Email": picking.partner_id.email or ' ',
                 "SMSNr": picking.partner_id.phone or ' '})
        return vals

    def _prepare_customs(self, picking):
        """@TODO 1- add a function to switch all values to EUR (POSTNL only accept EURO or USS)
            2- add a weight converter for diffrent types of UOM"""
        vals = {}
        _logger.info('getting customs for gloabl shippings only')
        vals.update({"Content": [{"CountryOfOrigin":  picking.company_id.country_id.code,
                                    "Description":  line.product_id.name,
                                    "Quantity":  line.product_uom_qty,
                                    "Value":  abs(line.value),
                                    "Weight":  line.weight} for line in picking.move_lines],
                                "Currency":  "EUR",
                                "HandleAsNonDeliverable":  "false",
                                "License":  "true",
                                "LicenseNr": self.picking.carrier_id.postnl_gloable_license_nr or ' ',
                                "ShipmentType":  "Commercial Goods"})
        _logger.info(vals)
        return vals

    def _prepare_customer_data(self, picking):
        vals = {}
        vals.update({"Address": {"AddressType":  "02",
                                 "City": picking.company_id.city or ' ',
                                 "CompanyName": picking.company_id.name or ' ',
                                 "Countrycode": picking.company_id.country_id.code or ' ',
                                 "HouseNr": picking.company_id.street2 or ' ',
                                 "Street": picking.company_id.street or ' ',
                                 "Zipcode":  picking.company_id.zip or ''},
                "CollectionLocation":  picking.company_id.zip or '',
                "ContactPerson":  picking.company_id.name or '',
                "CustomerCode":  picking.carrier_id.postnl_customer_code or '',
                "CustomerNumber": picking.carrier_id.postnl_customer_number or '',
                "Email": picking.company_id.email,
                "Name": picking.create_uid.name
                })
        return vals

    def _prepare_shipments_data(self, picking):
        vals = {}
        vals.update({"Addresses":  [self._prepare_shipments_addresses_data(picking)],
                      "Contacts":  [self._prepare_shipments_contacts_data(picking)],
                      "Dimension":  {"Weight":  str(sum([line.weight for line in picking.move_lines]))},
                      "ProductCodeDelivery":  self.get_product_code(picking)})
      
        if self.get_product_code(picking) == '4945':
            # customs ar required in globale shipping only and should't exist in other types
            vals["Customs"] = self._prepare_customs(picking)
        return vals

    def delivery_postnl_send_shipping(self, pickings):
        _logger.info('starting the ship PostNL Porcess')
        for picking in pickings:
            current_date = time.strftime('%d-%m-%Y %H: %M: %S')
            data = {
                "Customer":  self._prepare_customer_data(picking),
                "Message":  {"MessageID":  "01",
                            "MessageTimeStamp":  current_date,
                            "Printertype":  "GraphicFile|PDF"},
                "Shipments":  [self._prepare_shipments_data(picking)]
            }
            _logger.info('JSON body to the shipping api:  %s' % ((data)))
            response = PostNLRequets(self.api_key,self.prod_environment).ship(data)
            _logger.info('PostNL Response :  %s' % (response))

            # TODO insepct repsonse and get barcode and tracking_number and Generated file and add them to the stock.picking
            return [{"exact_price":  False,  "tracking_number":  False}]

    def send_shipping(self, picking):
        self.ensure_one()
        super().send_shipping(picking)
        self.delivery_postnl_send_shipping(picking)

    def delivery_postnl_cancel_shipment(self,  picking):
        raise UserError(_("Can Not Possible To Cancel PostNL Shipment!"))
