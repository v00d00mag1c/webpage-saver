from pydantic import Field, BaseModel
from typing import Any

class Webdriver(BaseModel):
    path: str = Field(default = None)
    platform: str = Field(default = 'win')
    executable_path: str = Field(default = None)
    user_data_dir: str = Field(default = None)

    _playwright: Any = None
    _browser: Any = None
    _crawler: Any = None
    _context: Any = None
