from fastapi import FastAPI
from app.routes import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(router)
origins = [
        "https://api.dbi-visual.eu/"
    ]

app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.on_event("startup")
async def startup_event():
    ## todo: do something about the trie, where to store it at runtime

    # Save the trie to a global variable
    print('WAKE THE FUCK UP SAMURAI, WE HAVE A CITY TO BURN')


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)