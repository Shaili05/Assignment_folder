"""
handlers.py


Turns errors into JSON responses so routers do not need their own try/except
blocks. Register once with register_exception_handlers(app).


Unknown errors are logged with the full traceback but the client only sees a
generic message, so internals and secrets never leave the server.
"""


import logging


from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


from src.exceptions.exceptions import AppError


logger = logging.getLogger(__name__)


def app_error_handler(request, exc):
    if exc.status_code >= 500:
        logger.error("%s on %s %s: %s", exc.error_code, request.method, request.url.path, exc.message)
    else:
        logger.warning("%s on %s %s: %s", exc.error_code, request.method, request.url.path, exc.message)
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())



def validation_error_handler(request, exc):
    details = [
        {"field": ".".join(str(part) for part in error["loc"][1:]), "message": error["msg"]}
        for error in exc.errors()
    ]
    logger.warning("validation_error on %s %s: %s", request.method, request.url.path, details)
    body = {"error": {"code": "validation_error", "message": "The request data is not valid.", "details": details}}
    return JSONResponse(status_code=422, content=body)



def unexpected_error_handler(request, exc):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    body = {"error": {"code": "internal_error", "message": "Something went wrong on the server."}}
    return JSONResponse(status_code=500, content=body)




def register_exception_handlers(app):
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unexpected_error_handler)



