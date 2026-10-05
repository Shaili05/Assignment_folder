from src.config.constants import ERROR_DEFINITIONS


class AppError(Exception):

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._apply_definition()

    @classmethod
    def _apply_definition(cls):
        definition = ERROR_DEFINITIONS.get(cls.__name__)
        if definition is not None:
            cls.status_code = definition["status_code"]
            cls.error_code = definition["error_code"]
            cls.default_message = definition["message"]

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)

    def to_dict(self):
        return {"error": {"code": self.error_code, "message": self.message}}


AppError._apply_definition()


class InvalidRequestError(AppError, ValueError):
    pass


class InvalidRoleError(InvalidRequestError):
    pass


class ReviewsNotFoundError(AppError):
    pass


class RateLimitError(AppError):
    pass


class LLMProviderError(AppError):
    pass


class AssistantTimeoutError(AppError):
    pass


class AssistantUnavailableError(AppError):
    pass


class VectorStoreUnavailableError(AppError):
    pass


class DataFileMissingError(AppError):
    pass


class ConfigurationError(AppError):
    pass


class ToolExecutionError(AppError):
    pass


class AgentExecutionError(AppError):
    pass
