# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


def resource_not_found(msg: str | None = None) -> dict:
    """Return an error message object for a resource that could not be found.

    This function will return a JSON serializable message for a resource that
    could not be found on the server. The optional msg argument can be used to
    provide a custom message in the response otherwise a generic message
    will be returned.

    Args:
        msg (str | None): Custom error message to return. Defaults to None.

    Returns:
        dict: An object that provides the error message.
    """
    return {"message": msg or "A resource could not be found on the server"}


def resource_already_exists(msg: str | None = None) -> dict:
    """Return an error message object for a resource that already exists.

    This function will return a JSON serializable message for a resource that
    already exists on the server. The optional msg argument can be used to
    provide a custom message in the response otherwise a generic message
    will be returned.

    Args:
        msg (str | None): Custom error message to return. Defaults to None.

    Returns:
        dict: An object that provides the error message.
    """
    return {"message": msg or "The specified resource already exists on the server"}


def bad_request(msg: str | None = None) -> dict:
    """Return an error message object for a bad request.

    This function will return a JSON serializable message for a bad request
    error. The optional msg argument can be used to provide a custom message
    in the response otherwise a generic message will be returned.

    Args:
        msg (str | None): Custom error message to return. Defaults to None.

    Returns:
        dict: An object that provides the error message.
    """
    return {"message": msg or "Bad Request"}


def internal_server_error(msg: str | None = None) -> dict:
    """Return an error message object for an internal server error.
    
    This function will return a JSON serializable message for an internal
    server error. The optional msg argument can be used to provide a custom
    message in the response otherwise a generic message will be returned.
    
    Args:
        msg (str | None): Custom error message to return. Defaults to None.
        
    Returns:
        dict: An object that provides the error message.
    """
    return {"message": msg or "Internal server error"}
