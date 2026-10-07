from fastapi import Request


DEFAULT_LIMIT = 10
DEFAULT_PAGE = 0


def read_page(request: Request) -> tuple:
    """(limit, page, offset) da query string; o schema já garantiu que são números válidos."""
    limit = int(request.query_params.get("limit", DEFAULT_LIMIT))
    page = int(request.query_params.get("page", DEFAULT_PAGE))

    return limit, page, page * limit


def page_envelope(page_result: dict, limit: int, page: int) -> dict:
    return {
        "data": page_result["data"],
        "limit": limit,
        "page": page,
        "is_last_page": page_result["is_last_page"],
    }
