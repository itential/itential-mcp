# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


def tostr(s: str | None) -> str:
    """Convert a value to a string representation.
    
    Args:
        s (str | None): The value to attempt to convert to a string.
        
    Returns:
        str: The string representation of the value, or None if input is None.
        
    Raises:
        None
    """
    if s is not None:
        s = str(s)
    return s


def tobytes(s: str | None, encoding: str = "utf-8") -> bytes:
    """Convert a string into bytes using the specified encoding.
    
    Args:
        s (str | None): The input string to convert.
        encoding (str): The character encoding to use (default is 'utf-8').
        
    Returns:
        bytes: The encoded byte representation of the string.
        
    Raises:
        AttributeError: If s is None and encode() is called on None.
        UnicodeEncodeError: If the string cannot be encoded with the specified encoding.
    """
    return s.encode(encoding)


def toint(value: str | None) -> int:
    """Convert a string representation of an integer to an int type.
    
    Args:
        value (str | None): A string to convert to integer.
        
    Returns:
        int: The integer value.
        
    Raises:
        ValueError: If the string cannot be converted to an integer.
        TypeError: If value is None.
    """
    return int(value)


def tobool(value: str | None) -> bool:
    """Convert a string representation of a boolean to a bool type.
    
    Args:
        value (str | None): A string like "true", "false", "1", "0", etc.
        
    Returns:
        bool: The boolean value corresponding to the input. Returns False if
            value is None or not a recognized boolean string.
            
    Raises:
        AttributeError: If value is not None or a string and strip() is called.
    """
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    return value.strip().lower() in {"true", "1", "yes", "on"}
