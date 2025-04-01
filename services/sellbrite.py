import requests

def get_product_by_sku(sku, sellbrite_api_key):
    headers = {
        'Authorization': f'Bearer {sellbrite_api_key}'
    }
    url = f"https://api.sellbrite.com/v1/products?sku={sku}"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        return data[0] if data else None
    raise Exception(f"Sellbrite error: {r.text}")

def delete_ebay_listing(product_id, sellbrite_api_key):
    headers = {
        'Authorization': f'Bearer {sellbrite_api_key}'
    }
    url = f"https://api.sellbrite.com/v1/listings/ebay/{product_id}"
    r = requests.delete(url, headers=headers)
    if r.status_code not in [200, 204]:
        raise Exception(f"Failed to delete listing: {r.text}")

def relist_item(product_id, sellbrite_api_key):
    headers = {
        'Authorization': f'Bearer {sellbrite_api_key}',
        'Content-Type': 'application/json'
    }
    url = f"https://api.sellbrite.com/v1/listings/ebay"
    data = {
        "product_id": product_id
    }
    r = requests.post(url, headers=headers, json=data)
    if r.status_code != 201:
        raise Exception(f"Failed to relist: {r.text}")
