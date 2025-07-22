import uvicorn

from rest.app import App

app = App().app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
