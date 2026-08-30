import json
from datetime import datetime
import time
from functools import wraps
from http.client import RemoteDisconnected
from typing import List, Optional, Literal
from urllib.parse import quote
import httpx


from .endpoints import (
    MeadowEndpoints, IamIntercomEndpoints
)
from .schemas import (
    Order, NewUser, AWSDocumentRequest, MeadowNewDocument, Product,
    Option, Reconciliation, UpdatePurchaseOrderLineItem,
    ReceiveLineItem, CreatePurchaseOrderLineItem, Address, LatLng
)
from .exceptions import (
    CreateUserException, CreateIDException, AuthenticationException, InvalidRequestException, ConnectionException,
    ResponseParseException
)



def handle_disconnect(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(5):
            try:
                return func(*args, **kwargs)

            except httpx.TransportError as e:
                print(f"HTTP error ({attempt + 1}/5): {e}")

                if attempt < 4:
                    time.sleep(0.25)

        raise ConnectionException("Unable to maintain connection to API")

    return wrapper



class MeadowClient(httpx.Client):

    def __init__(self, username=None, password=None, organization=None):
        super().__init__()
        if username and password:
            self.username = username
            self.password = password
            status_code, login_res = self.login()
            if status_code != 200:
                raise AuthenticationException(str(login_res))
            self.user_id = login_res["userId"]
            self.application_id = login_res["applicationId"]
            self.token = login_res["token"]
            self.updated_at = login_res["updatedAt"]
            self.created_at = login_res["createdAt"]
            self.id = login_res["id"]
            self.headers.update({"Authorization": f"token {self.token}"})
            self.headers.update({"Accept": "application/vnd.meadow+json; version=1"})
            # after login headers and tokens set
            self.roles = self.get_roles()[1]
            self.org_id = self.roles['organizations'][0]['id']
        # elif api_key and client_key:
        #     self.headers.update({"X-Consumer-Key":  api_key, "X-Client-Key": client_key})
        else:
            raise AuthenticationException("Username and password")

        if organization:
            self.change_org_by_name(organization)


    @handle_disconnect
    def post(self, *args, **kwargs) -> tuple[int, dict|list|bytes]:
        s, r = MeadowClient._get_result_from_response(super().post(*args, **kwargs))
        return s, r

    @handle_disconnect
    def get(self, *args, **kwargs) -> tuple[int, dict|list|bytes]:
        return MeadowClient._get_result_from_response(super().get(*args, **kwargs))

    @handle_disconnect
    def put(self, *args, **kwargs) -> tuple[int, dict]:
        s, r = MeadowClient._get_result_from_response(super().put(*args, **kwargs))
        if not isinstance(r, dict):
            raise ResponseParseException("Expected `dict` instance in response")
        return s, r


    @handle_disconnect
    def delete(self, *args, **kwargs) -> tuple[int, dict]:
        s, r =  MeadowClient._get_result_from_response(super().put(*args, **kwargs))
        if not isinstance(r, dict):
            raise ResponseParseException("Expected `dict` instance in response")
        return s, r

    @staticmethod
    def _get_result_from_response(response: httpx.Response) -> tuple[int, dict|bytes]:
        try:
            result_data = response.json()
            if "data" in result_data:
                result = result_data['data']
            elif "error" in result_data:
                result = result_data['error']
            else:
                result = result_data
            return response.status_code, result
        except:
            return response.status_code, response.content



    def login(self) -> tuple[int, dict]:
        """
        Logs the user in
        :return: status code and response data
        """
        return self.put(
            MeadowEndpoints.token,
            json={"emailOrPhone": self.username, "password": self.password},
        )

    def create_brand(self, name: str) -> tuple[int, dict]:
        """
        creates a brand
        :param name: name of the brand
        :return: status code and response data
        """
        s, r = self.post(MeadowEndpoints.brands.format(org_id=self.org_id), json={"name": name})
        if not isinstance(r, dict):
            raise ResponseParseException("Expected `dict` instance in response")
        return s, r

    def get_users(self, starting_after_id=None, user_type="adult-use"):
        params = {"type": user_type}
        if starting_after_id is not None:
            params['startingAfterId'] = starting_after_id
        return self.get(MeadowEndpoints.users.format(org_id=self.org_id), params=params)


    def get_brands(self) -> tuple[int, list]:
        s, r = self.get(MeadowEndpoints.brands.format(org_id=self.org_id))
        if not isinstance(r, list):
            raise ResponseParseException("Expected `list` instance in response")
        return s, r

    def get_purchase_orders(self, starting_after: int | None = None)-> tuple[int, list]:
        params = {}
        if starting_after:
            params['startingAfter'] = starting_after
        s, r = self.get(MeadowEndpoints.purchase_orders.format(org_id=self.org_id), params=params)
        if not isinstance(r, list):
            raise ResponseParseException("Expected `list` instance in response")
        return s, r

    def get_purchase_order(self, po_id: int) -> tuple[int, dict]:
        s, r = self.get(MeadowEndpoints.purchase_order.format(org_id=self.org_id, po_id=po_id))
        if not isinstance(r, dict):
            raise ResponseParseException("Expected `dict` instance in response")
        return s, r

    def get_product_categories(self) -> tuple[int, list]:
        s, r = self.get(MeadowEndpoints.all_product_categories.format(org_id=self.org_id))
        if not isinstance(r, list):
            raise ResponseParseException("Expected `list` instance in response")
        return s, r

    def get_vendors(self) -> tuple[int, list]:
        s, r = self.get(MeadowEndpoints.inventory_vendors.format(org_id=self.org_id))
        if not isinstance(r, list):
            raise ResponseParseException("Expected `list` instance in response")
        return s, r

    def get_vendor(self, vendor_id) -> tuple[int, dict]:
        s, r = self.get(MeadowEndpoints.inventory_vendor.format(org_id=self.org_id, vendor_id=vendor_id))
        if not isinstance(r, dict):
            raise ResponseParseException("Expected `dict` instance in response")
        return s, r

    def get_compliance_transfer(self, compliance_transfer_id) -> tuple[int, dict]:
        s, r =  self.get(MeadowEndpoints.compliance_transfer.format(org_id=self.org_id, compliance_transfer_id=compliance_transfer_id))
        if not isinstance(r, dict):
            raise ResponseParseException("Expected `dict` instance in response")
        return s, r

    def get_compliance_transfers(self, package_status: str = "ready") -> tuple[int, list]:
        params = {"packageStatus": package_status}
        s, r = self.get(MeadowEndpoints.compliance_transfers.format(org_id=self.org_id), params=params)
        if not isinstance(r, list):
            raise ResponseParseException("Expected `list` instance in response")
        return s, r

    def get_packages(self, package_status="ready", include_product_data: bool = True) -> tuple[int, list]:
        params = {"status": package_status, "includeProductData": include_product_data}
        s, r = self.get(MeadowEndpoints.packages.format(org_id=self.org_id), params=params)
        if not isinstance(r, list):
            raise ResponseParseException("Expected `list` instance in response")
        return s, r

    def get_full(self) -> tuple[int, dict]:
        s, r = self.get(MeadowEndpoints.full.format(org_id=self.org_id))
        if not isinstance(r, dict):
            raise ResponseParseException("Expected `dict` instance in response")
        return s, r

    def get_inventory_locations(self) -> tuple[int, list]:
        s, r = self.get(MeadowEndpoints.inventory_locations.format(org_id=self.org_id))
        if not isinstance(r, list):
            raise ResponseParseException("Expected `list` instance in response")
        return s, r

    def get_my_user_data(self) -> tuple[int, dict]:
        s, r = self.get(MeadowEndpoints.me)
        if not isinstance(r, dict):
            raise ResponseParseException("Expected `dict` instance in response")
        return s, r

    def get_roles(self) -> tuple[int, dict]:
        s, r = self.get(MeadowEndpoints.roles)
        if not isinstance(r, dict):
            raise ResponseParseException("Expected `dict` instance in response")
        return s, r

    def get_pusher_auth(self, socket_id, channel_name="private-marketing-1493"):
        return self.post(
            MeadowEndpoints.pusher_auth,
            data={
                "channel_name": channel_name,
                "socket_id": socket_id
            }
        )[1]['auth']

    def get_iam_data(self) -> tuple[int, dict]:
        _, user_data = self.get_my_user_data()
        _, roles = self.get_roles()
        s, r = self.post(IamIntercomEndpoints.web_ping,
                         data={
                             "app_id": "",
                             "platform": "web",
                             "installation_type": "js-snippet",
                             "internal": "{}",
                             "is_intersection_booted": "false",
                             "page_title": "Meadow",
                             "user_active_company_id": "undefined",
                             "user_data": json.dumps({
                                 "email": user_data["email"],
                                 "user_id": user_data["hashId"],
                                 "user_hash": roles['intercomUserHash'],
                                 "name": "Sebastian Campos"
                             }),
                             "source": "apiBoot",
                             "sampling": "false",
                             "referer": "https://admin.getmeadow.com/",
                         })
        if not isinstance(r, dict):
            raise ResponseParseException("Expected `dict` instance in response")
        return s, r

    def get_orders(
            self,
            status: Literal["draft", "new", "packed", "fulfilled", "canceled", "all"] = "new"
    ) -> tuple[int, list]:

        s, r = self.get(MeadowEndpoints.orders.format(org_id=self.org_id), params={"status": status})
        if not isinstance(r, list):
            raise ResponseParseException("Expected `list` instance in response")
        return s, r

    def get_order(self, order_id: int) -> tuple[int, dict]:
        s, r = self.get(MeadowEndpoints.orders.format(org_id=self.org_id) + "/" + str(order_id))
        if not isinstance(r, dict):
            raise ResponseParseException("Expected `dict` instance in response")
        return s, r


    def get_purchase_order_payments(self, po_id: int) -> tuple[int, list]:
        s, r = self.get(MeadowEndpoints.purchase_order_payment.format(org_id=self.org_id, po_id=po_id))
        if not isinstance(r, list):
            raise ResponseParseException("Expected `list` instance in response")
        return s, r


    def update_order_status(self, order_id, status: Literal["new", "packed", "fulfilled"], is_admin=True) -> tuple[int, dict]:
        payload = {}
        if is_admin:
            payload['isAdmin'] = is_admin
        if status == "canceled":
            raise InvalidRequestException("Invalid status Use client.cancel_order instead")
        payload['status'] = status
        return self.put(MeadowEndpoints.order.format(org_id=self.org_id, order_id=order_id), json=payload)


    def create_product_category(self, name: str, cannabis_type: str) -> tuple[int, dict]:
        s, r = self.post(
            MeadowEndpoints.product_categories.format(org_id=self.org_id),
            json={"name": name, "cannabisType": cannabis_type},
        )
        if not isinstance(r, dict):
            raise ResponseParseException("Expected `dict` instance in response")
        return s, r

    def create_vendor(
            self,
            name,
            seller_permit_number,
            notes,
            street1,
            postal_code,
            city,
            state,
            phone = "",
            street2 = "",

    )-> tuple[int, dict]:
        payload = {
            "name": name,
            "sellerPermitNumber": seller_permit_number,
            "notes": notes,
            "phone": phone,
            "street1": street1,
            "postalCode": postal_code,
            "city": city,
            "state": state,
        }
        if street2:
            payload['street2'] = street2
        s, r = self.post(MeadowEndpoints.vendors.format(org_id=self.org_id), json=payload)
        if not isinstance(r, dict):
            raise ResponseParseException("Expected `dict` instance in response")
        return s, r


    def create_product(self, product: dict | Product) -> tuple[int, dict]:
        if isinstance(product, dict):
            product = Product(**product)
        s, r = self.post(MeadowEndpoints.products.format(org_id=self.org_id), json=product.model_dump(by_alias=True))
        if not isinstance(r, dict):
            raise ResponseParseException("Expected `dict` instance in response")
        return s, r

    def create_purchase_order(
            self,
            inventory_vendor_id: int,
            expected_at: str,
            line_items: List[dict | CreatePurchaseOrderLineItem],
            external_invoice_number: Optional[str] = None,
            payment_terms_due_date: Optional[str] = None,
            shipping_handling_fee: Optional[int] = 0,
            shipping_handling_fee_excise: Optional[int] = 0
    ) -> tuple[int, dict]:
        line_items = [
            CreatePurchaseOrderLineItem(**i).model_dump(by_alias=True) if isinstance(i, dict) else i.model_dump(by_alias=True)
            for i in line_items
        ]
        payload = {
            "inventoryVendorId": inventory_vendor_id,
            "expectedAt": expected_at,
            "paymentTermsDueDate": payment_terms_due_date,
            "externalInvoiceNumber": external_invoice_number,
            "shippingHandlingFee": shipping_handling_fee,
            "shippingHandlingFeeExcise": shipping_handling_fee_excise,
            "lineItems": line_items
        }
        s, r = self.post(
            MeadowEndpoints.purchase_orders.format(org_id=self.org_id), json=payload
        )
        if not isinstance(r, dict):
            raise ResponseParseException("Expected `dict` instance in response")
        return s, r

    def update_purchase_order(
            self,
            po_number: int,
            inventory_vendor_id: int,
            expected_at: str,
            line_items: List[dict | UpdatePurchaseOrderLineItem],
            payment_status: str = "unpaid",
            payment_terms: Optional[str] = None,
            external_invoice_number: Optional[str] = None,
            payment_terms_due_date: Optional[str] = None,
            shipping_handling_fee: Optional[int] = 0,
            shipping_handling_fee_excise: Optional[int] = 0,
            notes: Optional[str] = None,
            status: str = "open"
    ) -> tuple[int, dict]:
        line_items = [
            UpdatePurchaseOrderLineItem(**i).model_dump(by_alias=True) if isinstance(i, dict) else i.model_dump(by_alias=True)
            for i in line_items
        ]

        payload = {
            "inventoryVendorId": inventory_vendor_id,
            "expectedAt": expected_at,
            "paymentStatus": payment_status,
            "paymentTerms": payment_terms,
            "paymentTermsDueDate": payment_terms_due_date,
            "notes": notes,
            "externalInvoiceNumber": external_invoice_number,
            "status": status,
            "shippingHandlingFee": shipping_handling_fee,
            "shippingHandlingFeeExcise": shipping_handling_fee_excise,
            "lineItems": line_items
        }
        return self.put(
            MeadowEndpoints.purchase_order.format(org_id=self.org_id, po_id=po_number), json=payload
        )

    def receive_line_items(self, inventory_location_id: int, po_id: int, line_items: List[ReceiveLineItem | dict]) -> tuple[int, dict]:
        line_items = [
            ReceiveLineItem(**i).model_dump(by_alias=True, exclude_none=True) if isinstance(i, dict) else i.model_dump(by_alias=True, exclude_none=True)
            for i in line_items
        ]
        payload = {
            "inventoryLocationId": inventory_location_id,
            "lineItems": line_items
        }

        s, r = self.post(
            MeadowEndpoints.purchase_order_receive.format(org_id=self.org_id, po_id=po_id), json=payload
        )
        if not isinstance(r, dict):
            raise ResponseParseException("Expected `dict` instance in response")
        return s, r

    def update_purchase_order_status(self, po_id: int, status: str):
        payload = {"status": status}
        return self.put(MeadowEndpoints.purchase_order.format(org_id=self.org_id, po_id=po_id), json=payload)

    def post_purchase_order_payment(self, po_id: int, amount: int, payment_type: str, payment_date: Optional[str] = None):
        payload = {"paymentDate":payment_date,"amount":amount, "paymentType": payment_type}
        return self.post(MeadowEndpoints.purchase_order_payment.format(org_id=self.org_id, po_id=po_id), json=payload)

    def metrc_refresh(self) -> tuple[int, dict]:
        s, r = self.post(MeadowEndpoints.metrc_compliance_transfer_sync.format(org_id=self.org_id))
        if not isinstance(r, dict):
            raise ResponseParseException("Expected `dict` instance in response")
        return s, r


    def change_org_by_name(self, name: str):
        organizations = self.roles['organizations']
        if new_org_context := next(filter(lambda o: o['name'] == name, organizations), None):
            self.org_id = new_org_context['id']
        else:
            raise InvalidRequestException(f"Name: {name}, not found in {', '.join([i['name'] for i in organizations])}")

    def get_reports(self, status="new") -> tuple[int, list]:
        s, r =  self.get(MeadowEndpoints.reports.format(org_id=self.org_id), params={"status": status})
        if not isinstance(r, list):
            raise ResponseParseException("Expected a `list` from this endpoint")
        return s, r

    def download_report(self, report_id: int) -> bytes:
        _, url = self.get(MeadowEndpoints.reports.format(org_id=self.org_id) + f"/{report_id}/url")
        if not isinstance(url, bytes):
            raise ResponseParseException("Expected a `str` from this endpoint")
        r = httpx.get(url.decode())
        return r.content

    def get_user_data(self, user_id):
        return self.get(MeadowEndpoints.users.format(org_id=self.org_id) + "/" + str(user_id))

    def get_recent_user_addresses(self, user_id):
        return self.get(MeadowEndpoints.recent_address.format(org_id=self.org_id, user_id=user_id))

    def cancel_order(self, order_id, cancel_msg: str, adjust_shift: bool = False):
        payload = {"cancelationReason": cancel_msg, "adjustShift": adjust_shift, "status": "canceled"}
        return self.put(MeadowEndpoints.orders.format(org_id=self.org_id) + "/" + order_id, json=payload)

    def create_order(self, meadow_order: Order | dict):
        if isinstance(meadow_order, Order):
            data = meadow_order.model_dump(by_alias=True, exclude_none=True)
        else:
            data = Order(**meadow_order).model_dump(by_alias=True, exclude_none=True)
        return self.post(MeadowEndpoints.orders.format(org_id=self.org_id), json=data)

    def create_user(self, meadow_user: dict | NewUser):
        if isinstance(meadow_user, dict):
            meadow_user = NewUser(**meadow_user)
        status_code, result = self.post(MeadowEndpoints.users.format(org_id=self.org_id), json=meadow_user.model_dump(by_alias=True))
        if status_code != 201:
            print("Error creating order", result)
            raise CreateUserException(f"{result}")
        return result

    def delete_document(self, document_id: int, user_id: int):
        return self.delete(MeadowEndpoints.user_documents.format(org_id=self.org_id, user_id=user_id) + "/" + str(document_id))

    def get_document(self, user_id, document_id) -> tuple[str, bytes]:
        _, document = self.get(
            MeadowEndpoints.user_documents.format(org_id=self.org_id, user_id=user_id) + f'/{document_id}',
        )
        if not isinstance(document, dict):
            raise ResponseParseException("Expected a `dict` from this endpoint")
        s3_url = document['signedUrl']
        mime_type = document['mime']
        doc_bytes = httpx.get(s3_url).content
        return mime_type, doc_bytes

    def upload_document(
            self,
            document: dict | AWSDocumentRequest,
            document_type_id: int,
            image: bytes,
            user_id: int,
            mime_type: str
    ) -> tuple[int, dict]:
        if isinstance(document, dict):
            document = AWSDocumentRequest(**document).model_dump(by_alias=True, exclude_none=True)
        else:
            document = document.model_dump(by_alias=True, exclude_none=True)

        _, signed_res = self.post(MeadowEndpoints.sign_s3.format(org_id=self.org_id), json=document)
        url = signed_res['signedRequest']['url']
        payload = signed_res['signedRequest']['fields']
        files = {'file': ('test.jpg', image, mime_type)}
        image_post_res = httpx.post(url, data=payload, files=files)
        if image_post_res.status_code != 204:
            raise CreateIDException(str(image_post_res.content.decode()))
        meadow_doc = MeadowNewDocument(
            documentTypeId=document_type_id,
            path=signed_res['path'],
            mime=mime_type
        )
        try_count = 0
        while True:
            try:
                status_code, meadow_post = self.post(
                    MeadowEndpoints.user_documents.format(org_id=self.org_id, user_id=user_id), json=meadow_doc.model_dump(by_alias=True),
                )
                if status_code != 201:
                    raise CreateIDException(str(meadow_post))
                elif not isinstance(meadow_post, dict):
                    raise ResponseParseException("Expected `dict` instance in response")
                return status_code, meadow_post
            except (ConnectionAbortedError, RemoteDisconnected) as e:
                time.sleep(3)
                try_count += 1
                if try_count >= 4:
                    raise CreateIDException(str(e))


    def delete_user(self, user_id):
        current_timestamp = datetime.utcnow().strftime(
            '%Y-%m-%dT%H:%M:%S.') + f"{int(datetime.utcnow().microsecond / 1000)}Z"
        payload = {
            "deletedAt": current_timestamp
        }
        return self.put(MeadowEndpoints.users.format(org_id=self.org_id) + f"/{user_id}", json=payload)

    def search_users(self, query):
        encoded_query = quote(query, safe="")
        return self.get(MeadowEndpoints.user_search.format(org_id=self.org_id) + f"?query={encoded_query}")

    def check_delivery_zone_address(
            self,
            address: Optional[dict | Address] = None,
            lat_and_lng: Optional[dict | LatLng] = None
    ):
        if isinstance(address, dict):
            address = Address(**address)
        if isinstance(lat_and_lng, dict):
            lat_and_lng = LatLng(**lat_and_lng)

        if address is not None:
            payload = {"address": address.model_dump(by_alias=True)}
        elif lat_and_lng is not None:
            payload = {"latLng": lat_and_lng.model_dump(by_alias=True)}
        else:
            raise InvalidRequestException("Must provide address or lat_and_lng")
        s, r = self.post(MeadowEndpoints.delivery_zone_addresses.format(org_id=self.org_id), json=payload)
        if not isinstance(r, list):
            raise ResponseParseException("Expected a `list` from this endpoint")
        return s, r

    def post_pricing(
            self,
            patient_hash,
            line_items: list[dict],
            tax_exempt: bool,
            delivery_zone_id: int | None,
            order_type: str
    ):
        pricing = {
            "adjustments": [],
            "discounts": [],
            "lineItems": line_items,
            "patientHash": patient_hash,
            "payments": [],
            "allowEmpty": True,
            "isAdmin": False,
            "taxExempt": tax_exempt,
            "deliveryZoneId": delivery_zone_id,
            "type": order_type
        }
        return self.post(MeadowEndpoints.pricing.format(org_id=self.org_id), json=pricing)

    @staticmethod
    def check_inventory_options(inventory_id, line_item):
        options = line_item['options']
        for o in options:
            for lc in o['locationInventory']:
                if lc['inventoryLocationId'] == inventory_id and lc['maxQuantity'] > 0:
                    return True
        return False

    @staticmethod
    def set_inventory_stock_value(inventory_id, line_item):
        options = line_item['options']
        line_item['in_stock'] = False
        for o in options:
            for lc in o['locationInventory']:
                if lc['inventoryLocationId'] == inventory_id and lc['maxQuantity'] > 0:
                    line_item['in_stock'] = True
        return line_item

    def get_inventory(
            self,
            inventory_id = None,
            include_archived: bool = True,
            include_moving_average_cost_per_unit: bool = True,
            include_threshold_status: bool = True,
            include_compliance_item_names: bool = True,
            filter_for_active: bool = True,
            filter_for_in_stock: bool = False,
            source="web-admin"
    ) -> list[dict]:
        payload = {
            "includeArchived": "true" if include_archived else "false",
            "includeMovingAverageCostPerUnit": "true" if include_moving_average_cost_per_unit else "false",
            "includeThresholdStatus": "true" if include_threshold_status else "false",
            "includeComplianceItemNames": "true" if include_compliance_item_names else "false",
            "source": source
        }
        _, line_items = self.get(MeadowEndpoints.inventory.format(org_id=self.org_id), params=payload)
        if not isinstance(line_items, list):
            raise ResponseParseException("Expected `list` instance in response")
        if filter_for_active:
            line_items = list(filter(lambda l: l['isActive'], line_items))
        if filter_for_in_stock and inventory_id:
            line_items = list(filter(lambda l: MeadowClient.check_inventory_options(inventory_id, l), line_items))
        if inventory_id:
            line_items = [MeadowClient.set_inventory_stock_value(inventory_id, l) for l in line_items]
        return line_items

    def get_discounts(self):
        return self.get(MeadowEndpoints.discounts.format(org_id=self.org_id))

    def get_product(self, product_id):
        return self.get(MeadowEndpoints.product.format(org_id=self.org_id, product_id=product_id))


    def get_inventory_transactions(
            self,
            product_id: Optional[int] = None,
            starting_after: Optional[str] = None,
    ) -> tuple[int, dict]:
        params = {}
        if product_id:
            params['productId'] = product_id
        if starting_after:
            params['startAfter'] = starting_after
        s, r = self.get(MeadowEndpoints.inventory_transactions.format(org_id=self.org_id), params=params)
        if not isinstance(r, dict):
            raise ResponseParseException("Expected `list` instance in response")
        return s, r


    def delete_product(self, product_id):
        current_timestamp = datetime.utcnow().strftime(
            '%Y-%m-%dT%H:%M:%S.') + f"{int(datetime.utcnow().microsecond / 1000)}Z"
        payload = {"deletedAt": current_timestamp}
        return self.put(MeadowEndpoints.product.format(org_id=self.org_id, product_id=product_id), json=payload)

    def update_product(self, product_id, product: dict | Product):
        if isinstance(product, dict):
            product = Product(**product)
        return self.put(
            MeadowEndpoints.product.format(org_id=self.org_id, product_id=product_id),
            json=product.model_dump(by_alias=True, exclude_none=True)
        )

    def update_product_options(self, product_id, options: List[dict | Option], sales_price_unit = None):
        options = [
            Option(**o).model_dump(by_alias=True, exclude_none=True) if isinstance(o,dict) else o.model_dump(by_alias=True, exclude_none=True)
            for o in options
        ]
        payload = {"options": options, "salesPriceUnit": sales_price_unit}
        return self.put(
            MeadowEndpoints.product_options.format(org_id=self.org_id, product_id=product_id),
            json=payload
        )

    def create_reconciliation(self, reconciliation: dict | Reconciliation):
        if isinstance(reconciliation, dict):
            reconciliation = Reconciliation(**reconciliation)
        return self.post(
            MeadowEndpoints.reconciliations.format(org_id=self.org_id),
            json=reconciliation.model_dump(by_alias=True)
        )