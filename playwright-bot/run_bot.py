from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bot.delete_listing import delete_listing_by_item_id

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
