# GetMeadow

A Python client for the [Meadow API](https://api-docs.getmeadow.com/introduction), built on `httpx` and `pydantic`.

Meadow's public Open API covers many admin-portal actions, but not all of them. This client supports both:

- **API key auth** (`api_key` and `client_key`) for the public API
- **Username and password** for login/admin features that are not in the public API

## Installation

```bash
pip install getmeadow
```

## Authentication

```python
import os
from getmeadow import MeadowClient

# Public API — each client key is tied to a single organization
client = MeadowClient(
    api_key=os.getenv("MEADOW_API_CONSUMER_KEY"),
    client_key=os.getenv("MEADOW_API_CLIENT_KEY"),
)

# Login / admin portal features
client = MeadowClient(
    username=os.getenv("MEADOW_USERNAME"),
    password=os.getenv("MEADOW_PASSWORD"),
    organization="Optional Org Name",  # optional; switches to this org after login
)
```

Calling a login-only method while using API keys raises `UnsupportedAPIFeatureException`.

## Response format

Most client methods return a two-item tuple of the HTTP status code and the response data:

```python
status_code, data = client.get_orders()
```

A few helpers, such as `get_inventory()`, return only the data.

## Organizations

In login mode, organization handling works like the Meadow web app. Requests use the client's current organization ID, and `client.change_org_by_name("Org Name")` switches the active organization. Available organizations are on `client.roles["organizations"]`.

API keys are issued for a single organization, so org switching is not available in API key mode. Use a separate client key for each org.

Most methods, such as `get_orders()`, operate on the currently selected organization.

## Example: create an order (login mode)

```python
import os
from getmeadow import MeadowClient

client = MeadowClient(
    username=os.getenv("MEADOW_USERNAME"),
    password=os.getenv("MEADOW_PASSWORD"),
)

order = {
    "type": "in-store",
    "status": "draft",
    "lineItems": [{
        "productId": 12345,
        "productOptionId": 678910,
        "quantity": 1,
    }],
    "payments": [{
        "paymentTypeId": 54321,
        "remaining": True,
    }],
    "patientHash": "9mLifw",
}
status_code, result = client.create_order(order)
```

In API key mode, `create_order` has no `status` field. Whether the order is created as a draft or as new depends on the organization's settings.

## Login-only features

These actions require username and password auth. They are not supported with API keys:

**Orders**

- Cancel an order
- Change an order's status
- Check whether an address is in a delivery zone
- Get a customer's recent addresses

**Customers**

- Create, delete, or search customers
- List the members of a customer group (the API can add or remove a customer, but cannot list members)
- Read or delete customer documents (the API can only upload)

**Products & inventory**

- Delete a product
- Create a product category
- Brands (list and create)
- Vendors (list, read one, or create)
- Inventory transaction history
- Inventory reconciliations
- Discounts

**Purchase orders**

- Read a single purchase order (the API can only list them)
- Receive line items
- Change a PO's status
- PO payments (read and create)

**Compliance (Metrc)**

- Read a single compliance transfer (the API can only list them)
- Trigger a Metrc sync

**Reporting**

- Sales, product, and customer insights
- Reports (list and download)

**Account & org**

- Full org config (payment types are available in the public API via `get_payment_types()`)
- Current user, roles, and permissions data
- Switching organizations
