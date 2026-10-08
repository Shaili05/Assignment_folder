import logging

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.config.constants import ERROR_DEFINITIONS
from src.exceptions.exceptions import AppError

logger = logging.getLogger(__name__)


def app_error_handler(request, exc):
    if exc.status_code >= 500:
        logger.error("%s on %s %s: %s", exc.error_code, request.method, request.url.path, exc.message)
    else:
        logger.warning("%s on %s %s: %s", exc.error_code, request.method, request.url.path, exc.message)
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())


def validation_error_handler(request, exc):
    definition = ERROR_DEFINITIONS["ValidationError"]
    details = [
        {"field": ".".join(str(part) for part in error["loc"][1:]), "message": error["msg"]}
        for error in exc.errors()
    ]
    logger.warning("%s on %s %s: %s", definition["error_code"], request.method, request.url.path, details)
    body = {
        "error": {
            "code": definition["error_code"],
            "message": definition["message"],
            "details": details,
        }
    }
    return JSONResponse(status_code=definition["status_code"], content=body)


def unexpected_error_handler(request, exc):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    error = AppError()
    return JSONResponse(status_code=error.status_code, content=error.to_dict())


def register_exception_handlers(app):
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unexpected_error_handler)
