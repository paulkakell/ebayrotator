from fastapi import FastAPI, Depends
from app import models, db, crud, auth
from app.services import ebay, sellbrite
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import threading
import time

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

@app.on_event("startup")
def startup_event():
    models.Base.metadata.create_all(bind=db.engine)
    threading.Thread(target=rotation_loop, daemon=True).start()

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
            ebay.scrape_and_delete_ended_listing(item_id)

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
