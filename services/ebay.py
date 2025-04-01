import requests
from app.crud import log_error
from bs4 import BeautifulSoup  # for future scraping logic

def get_active_listings(ebay_creds):
    headers = {
        'Authorization': f'Bearer {ebay_creds["access_token"]}',
        'Content-Type': 'application/json'
    }
    url = 'https://api.ebay.com/sell/inventory/v1/inventory_item'
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise Exception(f"eBay API error: {resp.text}")
    return resp.json()

def end_listing(item_id, ebay_creds):
    url = f"https://api.ebay.com/ws/api.dll"
    headers = {
        'X-EBAY-API-CALL-NAME': 'EndFixedPriceItem',
        'X-EBAY-API-SITEID': '0',
        'X-EBAY-API-COMPATIBILITY-LEVEL': '967',
        'X-EBAY-API-DEV-NAME': ebay_creds['dev_id'],
        'X-EBAY-API-APP-NAME': ebay_creds['app_id'],
        'X-EBAY-API-CERT-NAME': ebay_creds['cert_id'],
        'Content-Type': 'text/xml'
    }

    body = f"""<?xml version="1.0" encoding="utf-8"?>
    <EndFixedPriceItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
      <EndingReason>NotAvailable</EndingReason>
      <ItemID>{item_id}</ItemID>
      <RequesterCredentials>
        <eBayAuthToken>{ebay_creds['auth_token']}</eBayAuthToken>
      </RequesterCredentials>
    </EndFixedPriceItemRequest>
    """

    response = requests.post(url, data=body, headers=headers)
    if "<Ack>Failure</Ack>" in response.text:
        raise Exception(f"Failed to end listing: {response.text}")
    return True

def scrape_and_delete_ended_listing(item_id):
    # Placeholder for future Playwright/Puppeteer scraping logic
    # Needs session auth cookies or login automation
    print(f"TODO: Scrape eBay ended listings and delete item {item_id}")
    return True
