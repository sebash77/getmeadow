from .exceptions import UnsupportedAPIFeatureException


class _APIEndpointMeta(type):
    def __getattr__(cls, name: str):
        raise UnsupportedAPIFeatureException(
            f"{name} is not supported via the public Meadow API (API key mode). "
            "Use login credentials instead."
        )


class MeadowEndpoints:
    token = "https://admin.getmeadow.com/api/users/tokens"
    orders = "https://api.getmeadow.com/organizations/{org_id}/orders"
    order = "https://api.getmeadow.com/organizations/{org_id}/orders/{order_id}"
    pusher_auth = "https://api.getmeadow.com/pusher/auth"
    me = "https://api.getmeadow.com/users/me"
    roles = "https://api.getmeadow.com/users/me/roles"
    reports = "https://api.getmeadow.com/organizations/{org_id}/reports"
    inventory_locations = "https://api.getmeadow.com/organizations/{org_id}/inventory-locations"
    inventory_vendors = "https://api.getmeadow.com/organizations/{org_id}/inventory-vendors"
    inventory_vendor = "https://api.getmeadow.com/organizations/{org_id}/inventory-vendors/{vendor_id}"
    inventory = "https://daffodil.getmeadow.com/organizations/{org_id}/products/all"
    discounts = "https://api.getmeadow.com/organizations/{org_id}/discounts"
    delivery_zone_addresses = "https://api.getmeadow.com/organizations/{org_id}/delivery-zones/addresses"
    users = "https://api.getmeadow.com/organizations/{org_id}/users"
    inventory_transactions = " https://api.getmeadow.com/organizations/{org_id}/inventory-transactions"
    user_search = users + "/search"
    full = "https://api.getmeadow.com/organizations/{org_id}/full"
    user_documents = "https://api.getmeadow.com/organizations/{org_id}/users/{user_id}/documents"
    recent_address = "https://api.getmeadow.com/organizations/{org_id}/users/{user_id}/addresses/recent"
    pricing = "https://api.getmeadow.com/organizations/{org_id}/pricing"
    create_customer = "https://admin.getmeadow.com/customers/create"
    sign_s3 = "https://api.getmeadow.com/organizations/{org_id}/general/sign-s3"
    prod_document = "https://s3.us-west-2.amazonaws.com/meadow-documents-production"
    brands = "https://api.getmeadow.com/organizations/{org_id}/brands"
    products = "https://api.getmeadow.com/organizations/{org_id}/products"
    product = "https://api.getmeadow.com/organizations/{org_id}/products/{product_id}"
    product_options = "https://api.getmeadow.com/organizations/{org_id}/products/{product_id}/options"
    product_categories = "https://api.getmeadow.com/organizations/{org_id}/product-categories"
    all_product_categories = product_categories + "/all"
    purchase_orders = "https://api.getmeadow.com/organizations/{org_id}/purchase-orders"
    purchase_order = "https://api.getmeadow.com/organizations/{org_id}/purchase-orders/{po_id}"
    purchase_order_payment = "https://api.getmeadow.com/organizations/{org_id}/purchase-orders/{po_id}/payments"
    purchase_order_receive = "https://api.getmeadow.com/organizations/{org_id}/purchase-orders/{po_id}/receive"
    reconciliations = "https://api.getmeadow.com/organizations/{org_id}/reconciliations"
    vendors = "https://api.getmeadow.com/organizations/{org_id}/inventory-vendors"
    metrc_compliance_transfer_sync = "https://api.getmeadow.com/organizations/{org_id}/compliance-transfers/sync"
    compliance_transfers = "https://api.getmeadow.com/organizations/{org_id}/compliance-transfers"
    compliance_transfer = "https://api.getmeadow.com/organizations/{org_id}/compliance-transfers/{compliance_transfer_id}"
    packages = "https://api.getmeadow.com/organizations/{org_id}/packages"
    customer_groups = "https://api.getmeadow.com/organizations/{org_id}/customer-groups/"
    customer_group_users = "https://api.getmeadow.com/organizations/{org_id}/customer-groups/{group_id}/users"
    customer_group_user = "https://api.getmeadow.com/organizations/{org_id}/customer-groups/{group_id}/users/{user_id}"
    insights = "https://api.getmeadow.com/organizations/{org_id}/insights/v2/"
    product_insights = insights + "products"
    sales_insights = insights + "orders"
    customer_insights = insights + "demographics"


class MeadowAPIEndpoints(metaclass=_APIEndpointMeta):
    """Public Meadow Open API endpoints (api.getmeadow.com/api/v1).

    Authenticate with X-Consumer-Key + X-Client-Key headers (no login/token).
    Attribute names mirror MeadowEndpoints where an equivalent exists so the
    client can swap endpoint classes.
    """
    _api = "https://api.getmeadow.com/api/v1"
    _daffodil = "https://daffodil.getmeadow.com/api/v1"

    # Organization / analytics
    organization = _api + "/organization"
    orders = _api + "/orders"
    order = orders + "/{order_id}/detail"
    order_status = orders + "/{order_id}"
    order_returns = _api + "/order-returns"
    pricing = orders + "/pricing"
    inventory_locations = _api + "/inventory-locations"
    inventory = _daffodil + "/products/all"
    compliance_transfers = _api + "/compliance-transfers"
    packages = _api + "/packages"
    package = packages + "/{label}"
    purchase_orders = _api + "/purchase-orders"
    purchase_order = purchase_orders + "/{po_id}"
    instore_queues = _api + "/instore-queues"
    payment_types = _api + "/payment-types"
    payment_intents = _api + "/payment-intents"

    # Customers (mirrors MeadowEndpoints.users)
    users = _api + "/customers"
    user = users + "/{user_id}"
    customer_groups = _api + "/customer-groups"
    customer_group_add = customer_groups + "/{group_id}/add-customer"
    customer_group_remove = customer_groups + "/{group_id}/remove-customer"
    loyalty_events = _api + "/loyalty-events"
    user_documents = _api + "/documents/{user_id}/{document_type}"

    # Products / menu
    products = _api + "/products"
    product = products + "/{product_id}"
    product_options = product + "/options"
    product_options_upc = product_options + "/upc"
    product_categories = _api + "/product-categories"
    product_sub_categories = _api + "/product-sub-categories"
    menu = _daffodil + "/menu"
    product_tags = _daffodil + "/products/tags"


class IamIntercomEndpoints:
    web_ping = "https://api-iam.intercom.io/messenger/web/ping"
