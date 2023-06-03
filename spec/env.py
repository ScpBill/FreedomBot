import os
from abc import ABC
from typing import Final
from dotenv import load_dotenv


load_dotenv('./.env')


class Env(ABC):
    TOKEN: Final = os.environ.get('TOKEN', '0_0')
