from playwright.sync_api import sync_playwright
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Setting  # You can move or replicate model here

def get_db_settings():
    import os
    DB_URL = f"mariadb+mariadbconnector://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"
    engine = create_engine(DB_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    settings = {s.key: s.value for s in session.query(Setting).all()}
    session.close()
    return settings

def delete_listing_by_item_id(item_id):
    creds = get_db_settings()
    ebay_user = creds.get("ebay_username")
    ebay_pass = creds.get("ebay_password")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Login
        page.goto("https://www.ebay.com/signin/")
        page.fill("input#userid", ebay_user)
        page.click("button#signin-continue-btn")
        page.fill("input#pass", ebay_pass)
        page.click("button#sgnBt")

        # Navigate to Ended Listings
        page.goto("https://www.ebay.com/sh/lst/ended")
        page.wait_for_timeout(3000)
        
        # Search for item ID (logic to find and delete goes here)
        page.fill("input[placeholder='Search your listings']", item_id)
        page.press("input[placeholder='Search your listings']", "Enter")
        page.wait_for_timeout(5000)

        # You’d add logic here to find the delete icon/button and click it.
        # For now just snapshot to confirm:
        page.screenshot(path=f"/app/{item_id}_screen.png")

        context.close()
        browser.close()
