# GetMeadow

[API Documentation](https://api-docs.getmeadow.com/introduction)

## Installation

```bash
pip install getmeadow
```

A Python client for the Meadow API built on `httpx` and `pydantic`

GetMeadow uses Pydantic for request and response validation and currently supports username/password authentication.
Many client methods return a two-item tuple containing the HTTP status code and the response data:

```python
status_code, data = client.get_orders()
```

## Organizations
Organization handling works similarly to the Meadow web application.
API URLs are generated using the client instance's current organization ID. Calling `client.change_org_by_name` changes the active organization to the organization matching the provided name.
Organization data is available through the roles attribute:

`client.roles['organizations']`

Most API methods, such as get_orders() and create_user(), operate on the currently selected organization.
```python
    client = MeadowClient(
        username=os.getenv("MEADOW_USERNAME"),
        password=os.getenv("MEADOW_PASSWORD")
    )

    product_id = 12345
    product_option_id = 678910
    payment_type_id = 54321
    patient_hash = '9mLifw'

    order = {
        "type": "in-store",
        "status": "draft",
        "lineItems": [{
            "productId": product_id,
            "productOptionId": product_option_id,
            "quantity": 1
        }],
        "payments": [{
            'paymentTypeId': payment_type_id,
            'remaining': True,
        }],
        "patientHash": patient_hash
    }
    status_code, result = client.create_order(order)
```
