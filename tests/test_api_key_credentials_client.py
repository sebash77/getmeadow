import os
import random
from getmeadow import MeadowClient


def test_get_orders():
    client = MeadowClient(
        api_key=os.getenv("MEADOW_API_CONSUMER_KEY"),
        client_key=os.getenv("MEADOW_API_CLIENT_KEY_SENSI")
    )
    new_status_code, new = client.get_orders(status="new")
    fulfilled_status_code, fulfilled = client.get_orders(status="fulfilled")
    packed_status_code, packed = client.get_orders(status="packed")
    canceled_status_code, canceled = client.get_orders(status="canceled")
    draft_status_code, draft = client.get_orders(status="draft")

    status_codes = [new_status_code, new_status_code, fulfilled_status_code, packed_status_code, canceled_status_code, draft_status_code]
    assert all(map(lambda s: s == 200, status_codes)), "Unable to retrieve orders by status"


def test_create_order():
    client = MeadowClient(
        api_key=os.getenv("MEADOW_API_CONSUMER_KEY"),
        client_key=os.getenv("MEADOW_API_CLIENT_KEY_BAYCARE")
    )
    customers = client.get_customers()[1]
    valid_customers = list(filter(lambda c: c['email'] is not None or c['phone'] is not None, customers))
    _, inventory_locations = client.get_inventory_locations()
    default_location = next(filter(lambda loc: loc['name'] == 'Default Location', inventory_locations))
    while len(customers) >= 50 and len(valid_customers) == 0:
        customers = client.get_customers(starting_after_id=customers[-1]['id'])[1]
        valid_customers = list(filter(lambda c: c['email'] is not None or c['phone'] is not None, customers))

    u = random.choice(valid_customers)
    l = random.choice(client.get_inventory(filter_for_active=True, filter_for_in_stock=True, inventory_id=default_location['id']))
    o = random.choice([o for o in l['options'] if o['locationInventory']])
    p = random.choice(client.get_payment_types()[1])


    s, r = client.post_pricing(
        line_items= [{
            # "productId": o['productId'],
            "productOptionId": o['id'],
            "quantity": 1
        }],
        order_type="pickup",
        customer={
            "firstName": u['firstName'],
            "lastName": u['lastName'],
            "email": u['email'],
            "phone": u['phone'],
            "birthday": u['birthday'],
        }
    )

    order = {
        "type": "delivery",
        "lineItems": [{
            "productOptionId": o['id'],
            "quantity": 1
        }],
        "payments": [{
            'paymentTypeId': p['id'],
            'remaining': True,
        }],
        "customer": {
            "firstName": u['firstName'],
            "lastName": u['lastName'],
            "email": u['email'],
            "phone": u['phone'],
            "birthday": u['birthday'],
        },
        "address": u['mostRecentAddress'],
        "idempotencyKey": r['idempotencyKey']
    }

    s, r = client.create_order(order)

    assert s == 201, "Unable to create order"


    admin_client = MeadowClient(
        username=os.getenv("MEADOW_USERNAME"),
        password=os.getenv("MEADOW_PASSWORD")
    )

    s, r = admin_client.cancel_order(r['id'], "api order test")
    assert s == 200, "Unable to cancel order"