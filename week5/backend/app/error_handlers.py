from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def register_error_handlers(app: FastAPI) -> None:
    """Register global exception handlers that return consistent JSON envelopes."""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        code_map = {
            400: "BAD_REQUEST",
            404: "NOT_FOUND",
            409: "CONFLICT",
            422: "VALIDATION_ERROR",
        }
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "ok": False,
                "error": {
                    "code": code_map.get(exc.status_code, "HTTP_ERROR"),
                    "message": str(exc.detail),
                },
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        messages = []
        for err in exc.errors():
            loc = " -> ".join(str(l) for l in err["loc"])
            messages.append(f"{loc}: {err['msg']}")
        return JSONResponse(
            status_code=422,
            content={
                "ok": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "; ".join(messages),
                },
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred.",
                },
            },
        )
