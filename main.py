from fastapi import FastAPI
from app.routes import router
from app.models import Dictionary
from app.trie import Trie
from app.db import get_db2
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    # Retrieve all words from the database
    words = get_db2().query(Dictionary.word).all()

    # Create a new trie
    trie = Trie()

    # Insert each word into the trie
    for word in words:
        trie.insert(word)

    # Save the trie to a global variable
    app.state.trie = trie

if __name__ == "__main__":
    origins = [
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:3000",
        "http://localhost:4200",
        "https://dbi-visual.eu",
        "http://dbi-visual.eu"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
