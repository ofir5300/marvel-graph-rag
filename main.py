from dotenv import load_dotenv
import uvicorn

from dal.loaders import run_all_ETLs
from app.service import app

load_dotenv()
run_all_ETLs()

def main():
    # RedisService().reset_index()
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main() 