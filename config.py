import os
from pathlib import Path
from dotenv import load_dotenv
from exceptions import InvalidJsonConfigFileException


class SayadGanjConfig:
    def __init__(self):
        try:
            self.api_id, self.api_hash, self.token = self._read_env_config()
        except InvalidJsonConfigFileException:
            exit(2)

    def _read_env_config(self):
        load_dotenv(verbose=False)
        env_path = Path('./env') / '.env'
        load_dotenv(dotenv_path=str(env_path))

        api_id = os.getenv("API_ID")
        api_hash = os.getenv("API_HASH")
        token = os.getenv("TOKEN")

        return api_id, api_hash, token