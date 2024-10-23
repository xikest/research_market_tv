from fastapi import FastAPI
import uvicorn
import os
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello"}

@app.post("/items/{item_id}")
def read_item(item_id:int, q:str=None):
     return {"item_id": item_id, "q": q}
 

if __name__ == "__main__":
    uvicorn.run(app, port=int(os.environ.get("PORT", 8080)))