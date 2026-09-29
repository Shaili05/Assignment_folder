import pytest


from src.exceptions import exceptions as exc


ALL_ERRORS = [
    exc.InvalidRequestError, exc.InvalidRoleError, exc.ReviewsNotFoundError,
    exc.RateLimitError, exc.LLMProviderError, exc.AssistantTimeoutError,
    exc.AssistantUnavailableError, exc.VectorStoreUnavailableError,
    exc.DataFileMissingError, exc.ConfigurationError, exc.ToolExecutionError,
]




@pytest.mark.parametrize("error_class, status", [
    (exc.InvalidRequestError, 400),
    (exc.InvalidRoleError, 400),
    (exc.ReviewsNotFoundError, 404),
    (exc.RateLimitError, 429),
    (exc.LLMProviderError, 502),
    (exc.AssistantTimeoutError, 504),
    (exc.AssistantUnavailableError, 503),
    (exc.VectorStoreUnavailableError, 503),
    (exc.DataFileMissingError, 500),
    (exc.ConfigurationError, 500),
    (exc.ToolExecutionError, 500),
])
def test_status_codes(error_class, status):
    assert error_class.status_code == status




def test_every_error_derives_from_app_error():
    for error_class in ALL_ERRORS:
        assert issubclass(error_class, exc.AppError)




def test_error_codes_are_unique():
    codes = [error_class.error_code for error_class in ALL_ERRORS]
    assert len(codes) == len(set(codes))




def test_default_and_custom_message():
    assert exc.ReviewsNotFoundError().message == exc.ReviewsNotFoundError.default_message
    assert exc.ReviewsNotFoundError("No reviews for Oat Balm").message == "No reviews for Oat Balm"




def test_to_dict_shape():
    body = exc.RateLimitError("slow down").to_dict()
    assert body == {"error": {"code": "rate_limited", "message": "slow down"}}




def test_invalid_request_is_still_a_value_error():
    with pytest.raises(ValueError):
        raise exc.InvalidRequestError("bad aspect")
    assert issubclass(exc.InvalidRoleError, exc.InvalidRequestError)

