"""
exceptions.py


Domain errors raised by the services, tools and agent. Every error carries an
HTTP status code and a short machine-readable error code. main.py turns them
into JSON responses, so routers do not need their own try/except blocks.
"""


class AppError(Exception):
    status_code = 500
    error_code = "internal_error"
    default_message = "Something went wrong on the server."


    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)


    def to_dict(self):
        return {"error": {"code": self.error_code, "message": self.message}}


class InvalidRequestError(AppError, ValueError):
    status_code = 400
    error_code = "invalid_request"
    default_message = "The request is not valid."


class InvalidRoleError(InvalidRequestError):
    error_code = "invalid_role"
    default_message = "Unknown role."



class ReviewsNotFoundError(AppError):
    status_code = 404
    error_code = "reviews_not_found"
    default_message = "No reviews match the request."


class RateLimitError(AppError):
    status_code = 429
    error_code = "rate_limited"
    default_message = "The language model is rate limited. Please try again in a minute."


class LLMProviderError(AppError):
    status_code = 502
    error_code = "llm_provider_error"
    default_message = "The language model provider returned an error."



class AssistantTimeoutError(AppError):
    status_code = 504
    error_code = "assistant_timeout"
    default_message = "The assistant did not answer in time."



class AssistantUnavailableError(AppError):
    status_code = 503
    error_code = "assistant_unavailable"
    default_message = "The assistant is not available yet."



class VectorStoreUnavailableError(AppError):
    status_code = 503
    error_code = "vector_store_unavailable"
    default_message = "The review search index could not be opened."



class DataFileMissingError(AppError):
    status_code = 500
    error_code = "data_file_missing"
    default_message = "A required data file was not found."



class ConfigurationError(AppError):
    status_code = 500
    error_code = "configuration_error"
    default_message = "The application is not configured correctly."


class ToolExecutionError(AppError):
    status_code = 500
    error_code = "tool_execution_error"
    default_message = "A tool failed while running."

