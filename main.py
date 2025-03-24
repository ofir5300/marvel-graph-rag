from dotenv import load_dotenv
import uvicorn

from dal.loaders import run_all_ETLs
from api.api import app


def init_system():
    load_dotenv()
    # RedisService().reset_index()
    run_all_ETLs()
    # call("who is welveri") #  TODO make it sucess

def main():
    init_system()
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main() 