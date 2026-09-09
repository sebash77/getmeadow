import os
import random
from getmeadow import MeadowClient


def test_login():
    client = MeadowClient(
        username=os.getenv("MEADOW_USERNAME"),
        password=os.getenv("MEADOW_PASSWORD")
    )
    assert client.org_id, "Org ID not set, failed to login"


def test_get_orders():
    client = MeadowClient(
        username=os.getenv("MEADOW_USERNAME"),
        password=os.getenv("MEADOW_PASSWORD")
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
        username=os.getenv("MEADOW_USERNAME"),
        password=os.getenv("MEADOW_PASSWORD")
    )
    u = random.choice(client.get_customers()[1])
    l = random.choice(client.get_inventory())
    o = random.choice(l['options'])
    p = random.choice(client.get_full()[1]['paymentTypes'])
    order = {
        "type": "in-store",
        "status": "draft",
        "lineItems": [{
            "productId": o['productId'],
            "productOptionId": o['id'],
            "quantity": 1
        }],
        "payments": [{
            'paymentTypeId': p['id'],
            'remaining': True,
        }],
        "patientHash": u['hashId']
    }
    s, r = client.create_order(order)

    assert s == 201, "Unable to create draft order"

    s, r = client.cancel_order(r['id'], "draft order test")
    assert s == 200, "Unable to cancel draft order"


def test_get_delivery_zones():
    client = MeadowClient(
        username=os.getenv("MEADOW_USERNAME"),
        password=os.getenv("MEADOW_PASSWORD")
    )

    address = {
        'street1': '3414 25th St #17',
        'city': 'San Fransisco',
        'state': 'California',
        'postalCode': '94110',
        'county': None
    }

    lat_lng = {
        'lat': 37.751652,
        'lng': -122.417409,
    }

    s, r = client.check_delivery_zone_address(address=address)
    assert s == 200, "Unable to check delivery zone by address"

    s, r = client.check_delivery_zone_address(lat_and_lng=lat_lng)
    assert s == 200, "Unable to check delivery zone by lat/lng"