import uvicorn
from website.auth_api import app

if __name__ == "__main__":
    uvicorn.run("website.auth_api:app", host="127.0.0.1", port=8000, reload=True)
