import os
from dotenv import load_dotenv

from src.DBManagerClass import DBManager

load_dotenv()


def main():
    api_key_hh = os.getenv('API_KEY_HH')
    print(api_key_hh)

    hh = DBManager()


if __name__ == '__main__':
    main()
