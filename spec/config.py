from abc import ABC
from typing import Final


class Config(ABC):
    CMD_PREFIX: Final = '.'
    ID_GUILD: Final = 948239228989493338
    STANDARD_EXTENSIONS: Final = ['owner.loader', 'owner.sync']
