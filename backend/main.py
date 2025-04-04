from fastapi import FastAPI, BackgroundTasks,Depends
from app import models, db, crud, auth
from app.services import ebay, sellbrite
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import threading, time, requests, smtplib

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
)

# Dependency for DB
def get_db():
    db_sess = db.SessionLocal()
    try:
        yield db_sess
    finally:
        db_sess.close()
def daily_loop():
    while True:
        send_daily_error_summary()
        time.sleep(86400)  # 24 hours


@app.on_event("startup")
def startup_event():
    models.Base.metadata.create_all(bind=db.engine)
    threading.Thread(target=rotation_loop, daemon=True).start()
    threading.Thread(target=daily_loop, daemon=True).start()  # <-- this is new

@app.get("/status", dependencies=[Depends(auth.verify_api_key)])
def get_status(db: Session = Depends(get_db)):
    last = db.query(models.RotationStatus).order_by(models.RotationStatus.id.desc()).first()
    return {
        "last_run": last.last_run if last else None,
        "last_sku": last.last_sku if last else None,
        "success": last.success if last else None,
    }

@app.get("/errors", dependencies=[Depends(auth.verify_api_key)])
def get_errors(db: Session = Depends(get_db)):
    return db.query(models.ErrorLog).order_by(models.ErrorLog.timestamp.desc()).limit(50).all()

@app.get("/config", dependencies=[Depends(auth.verify_api_key)])
def get_config(db: Session = Depends(get_db)):
    return crud.get_settings(db)

@app.put("/config", dependencies=[Depends(auth.verify_api_key)])
def update_config(key: str, value: str, db: Session = Depends(get_db)):
    crud.set_setting(db, key, value)
    return {"message": "Updated"}

def rotation_loop():
    while True:
        db_sess = db.SessionLocal()
        try:
            settings = crud.get_settings(db_sess)
            sleep_minutes = int(settings.get("sleep_minutes", 5))

            ebay_creds = {
                "dev_id": settings.get("ebay_dev_id"),
                "app_id": settings.get("ebay_app_id"),
                "cert_id": settings.get("ebay_cert_id"),
                "auth_token": settings.get("ebay_auth_token"),
                "access_token": settings.get("ebay_access_token")
            }
            sellbrite_key = settings.get("sellbrite_api_key")

            listings = ebay.get_active_listings(ebay_creds)
            # Let's say the oldest is the first for now
            oldest_item = listings['inventoryItems'][0]
            item_id = oldest_item['sku']
            sku = oldest_item['sku']

            ebay.end_listing(item_id, ebay_creds)
            trigger_playwright_delete(item_id)

            product = sellbrite.get_product_by_sku(sku, sellbrite_key)
            if not product:
                raise Exception(f"SKU {sku} not found in Sellbrite")

            sellbrite.delete_ebay_listing(product['product_id'], sellbrite_key)
            sellbrite.relist_item(product['product_id'], sellbrite_key)

            crud.update_rotation_status(db_sess, sku=sku, success=True)

        except Exception as e:
            crud.log_error(db_sess, step="rotation_loop", message=str(e), sku=locals().get('sku', 'unknown'))
        finally:
            db_sess.close()
        time.sleep(sleep_minutes * 60)
        
def trigger_playwright_delete(item_id: str):
    try:
        response = requests.post(
            "http://playwright-bot:9000/delete-ended-listing",
            json={"item_id": item_id},
            timeout=30
        )
        if not response.ok:
            raise Exception(f"Playwright bot failed: {response.text}")
    except Exception as e:
        raise Exception(f"Error calling playwright-bot: {str(e)}")
def send_daily_error_summary():
    db_sess = db.SessionLocal()
    try:
        since = datetime.utcnow() - timedelta(days=1)
        errors = db_sess.query(models.ErrorLog).filter(models.ErrorLog.timestamp > since).all()
        if not errors:
            return

        body = "\n\n".join(f"{e.timestamp} - {e.step} - {e.sku} - {e.message}" for e in errors)
        creds = crud.get_settings(db_sess)
        email_to = creds.get("alert_email")

        if email_to:
            msg = MIMEText(body)
            msg["Subject"] = "eBay Bot Daily Error Report"
            msg["From"] = "bot@localhost"
            msg["To"] = email_to

            server = smtplib.SMTP("mailserver.local", 25)  # Or your relay
            server.sendmail("bot@localhost", [email_to], msg.as_string())
            server.quit()
    except Exception as e:
        crud.log_error(db_sess, "send_daily_summary", str(e))
    finally:
        db_sess.close()

from fastapi import BackgroundTasks

@app.post("/send-report", dependencies=[Depends(auth.verify_api_key)])
def send_report_now(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_daily_error_summary)
    return {"message": "Report is being sent."}
