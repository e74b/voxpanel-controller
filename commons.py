from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from typing import Literal, Union
from pydantic import BaseModel

success_short = lambda detail=None, **kwargs: {
    "status": "success",
    "detail": detail,
    **kwargs,
}

error_short = lambda detail=None, code=400, **kwargs: JSONResponse(
    status_code=code, content={"status": "error", "detail": detail, **kwargs}
)


class APIResponse(BaseModel):
    status: Literal["success", "error"]
    detail: Union[None, str]
