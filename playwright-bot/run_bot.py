from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import FileResponse
from pydantic import BaseModel
from bot.delete_listing import delete_listing_by_item_id
import os

app = FastAPI()

class DeleteRequest(BaseModel):
    item_id: str

@app.post("/delete-ended-listing")
def delete_ended_listing(request: DeleteRequest):
    try:
        result = delete_listing_by_item_id(request.item_id)
        return {"status": "ok", "item_id": request.item_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/screenshot/{item_id}")
def get_screenshot(item_id: str = Path(...)):
    # Look for most recent screenshot with that item_id prefix
    files = [f for f in os.listdir("/app") if f.startswith(item_id) and f.endswith(".png")]
    if not files:
        raise HTTPException(status_code=404, detail="Screenshot not found")
    latest_file = sorted(files)[-1]
    return FileResponse(f"/app/{latest_file}", media_type="image/png")
