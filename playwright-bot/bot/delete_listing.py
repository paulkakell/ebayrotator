from playwright.sync_api import sync_playwright
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import os
from datetime import datetime
from app.models import Setting  # You can move this locally if needed

def get_db_settings():
    DB_URL = f"mariadb+mariadbconnector://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"
    engine = create_engine(DB_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        settings = {s.key: s.value for s in session.query(Setting).all()}
    except SQLAlchemyError as e:
        print("DB Error:", e)
        settings = {}
    finally:
        session.close()
    return settings

def delete_listing_by_item_id(item_id):
    creds = get_db_settings()
    ebay_user = creds.get("ebay_username")
    ebay_pass = creds.get("ebay_password")
    if not ebay_user or not ebay_pass:
        raise Exception("Missing eBay username or password in settings")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # 1. Log into eBay
        page.goto("https://signin.ebay.com/")
        page.fill("input#userid", ebay_user)
        page.click("button#signin-continue-btn")
        page.wait_for_selector("input#pass")
        page.fill("input#pass", ebay_pass)
        page.click("button#sgnBt")

        # 2. Go to Ended Listings
        page.wait_for_url("**/myebay**", timeout=15000)
        page.goto("https://www.ebay.com/sh/lst/ended")
        page.wait_for_selector("input[placeholder='Search your listings']", timeout=10000)

        # 3. Search for Item ID
        page.fill("input[placeholder='Search your listings']", item_id)
        page.keyboard.press("Enter")
        page.wait_for_timeout(3000)

        # 4. Locate delete action for item
        item_row = page.query_selector(f"text={item_id} >> xpath=ancestor::div[contains(@class, 'list-row')]")
        if not item_row:
            raise Exception(f"Could not locate listing row for item ID: {item_id}")

        # Try clicking the "more actions" menu, then delete
        item_row.hover()
        item_row.click()

        # This may vary slightly depending on eBay layout and auth state
        page.click("button[aria-label='More actions']")
        page.wait_for_timeout(1000)
        page.click("text=Delete listing")

        # Confirm popup
        page.wait_for_selector("text=Yes, delete it", timeout=5000)
        page.click("text=Yes, delete it")

        # Snapshot for log/debug
        timestamp = datetime.utcnow().isoformat().replace(":", "_")
        page.screenshot(path=f"/app/{item_id}_{timestamp}.png")

        context.close()
        browser.close()
