from abc import ABC
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any, Self

from boxed.error import UnwrapError


@dataclass
class _Result[T, E](ABC):
    """
    Result[T, E] represents a value that may or may not be valid.

    Examples
    --------
    >>> Ok(1)
    Ok(1)
    >>> Err("Error")
    Err('Error')
    >>> Ok(1).is_ok()
    True
    >>> Err("Error").is_ok()
    False
    >>> Ok(1).is_err()
    False
    >>> Err("Error").is_err()
    True
    >>> Ok(1).unwrap()
    1
    >>> Err("Error").unwrap()
    Traceback (most recent call last):
        ...
    boxed.error.UnwrapError: Error
    >>> Ok(1).unwrap_or(2)
    1
    >>> Err("Error").unwrap_or(2)
    2
    >>> Ok(1).unwrap_or_else(lambda: 2)
    1
    >>> Err("Error").unwrap_or_else(lambda: 2)
    2
    >>> Ok(1).expect("Error")
    1
    >>> Err("Error").expect("Error")
    Traceback (most recent call last):
        ...
    boxed.error.UnwrapError: Error
    """

    value: T | E

    def unwrap(self) -> T:
        """
        >>> Ok(1).unwrap()
        1
        >>> Err("Error").unwrap()
        Traceback (most recent call last):
            ...
        boxed.error.UnwrapError: Error
        """
        match self:
            case Ok(value):
                return value
            case Err(msg):
                raise UnwrapError(msg)
            case _:
                raise TypeError(f"Result can only be either Ok or Err, not {type(self)}")

    def expect(self, msg: str, /) -> T:
        """
        >>> Ok(1).expect("Error")
        1
        >>> Err("Error").expect("Error")
        Traceback (most recent call last):
            ...
        boxed.error.UnwrapError: Error
        """
        match self:
            case Ok(value):
                return value
            case Err(_):
                raise UnwrapError(msg)
            case _:
                raise TypeError(f"Result can only be either Ok or Err, not {type(self)}")

    def unwrap_or(self, default: T, /) -> T:
        """
        >>> Ok(1).unwrap_or(2)
        1
        >>> Err("Error").unwrap_or(2)
        2
        """
        match self:
            case Ok(value):
                return value
            case Err(_):
                return default
            case _:
                raise TypeError(f"Result can only be either Ok or Err, not {type(self)}")

    def unwrap_or_else(self, default: Callable[[], T], /) -> T:
        """
        >>> Ok(1).unwrap_or_else(lambda: 2)
        1
        >>> Err("Error").unwrap_or_else(lambda: 2)
        2
        """
        match self:
            case Ok(value):
                return value
            case Err(_):
                return default()
            case _:
                raise TypeError(f"Result can only be either Ok or Err, not {type(self)}")

    def is_ok(self) -> bool:
        """
        >>> Ok(1).is_ok()
        True
        >>> Err("Error").is_ok()
        False
        """
        match self:
            case Ok(_):
                return True
            case Err(_):
                return False
            case _:
                raise TypeError(f"Result can only be either Ok or Err, not {type(self)}")

    def is_err(self) -> bool:
        """
        >>> Ok(1).is_err()
        False
        >>> Err("Error").is_err()
        True
        """
        match self:
            case Ok(_):
                return False
            case Err(_):
                return True
            case _:
                raise TypeError(f"Result can only be either Ok or Err, not {type(self)}")

    def map[U](self, mapper: Callable[[T], U], /) -> "Result[U, E]":
        """
        >>> Ok(1).map(lambda x: x + 1)
        Ok(2)
        >>> Err("Error").map(lambda x: x + 1)
        Err('Error')
        """
        match self:
            case Ok(value):
                return Ok(mapper(value))
            case Err(_):
                return self
            case _:
                raise TypeError(f"Result can only be either Ok or Err, not {type(self)}")

    def map_err[E_New](self, mapper: Callable[[E], E_New], /) -> "Result[T, E_New]":
        """
        >>> Ok(1).map_err(lambda x: x + 1)
        Ok(1)
        >>> Err("Error").map_err(lambda x: x.upper())
        Err('ERROR')
        """
        match self:
            case Err(error):
                return Err(mapper(error))
            case Ok(_):
                return self
            case _:
                raise TypeError(f"Result can only be either Ok or Err, not {type(self)}")

    def and_then[U](self, mapper: Callable[[T], "Result[U, E]"], /) -> "Result[U, E]" | Self:
        """
        >>> Ok(1).and_then(lambda x: Ok(x + 1))
        Ok(2)
        >>> Ok(1).and_then(lambda x: Err("Error"))
        Err('Error')
        >>> Err("Error").and_then(lambda x: Ok(x + 1))
        Err('Error')
        """
        match self:
            case Ok(value):
                return mapper(value)
            case Err(_):
                return self
            case _:
                raise TypeError(f"Result can only be either Ok or Err, not {type(self)}")

    def __bool__(self) -> bool:
        return self.is_ok()

    def __eq__(self, other: object) -> bool:
        match self, other:
            case (Ok(a), Ok(b)):
                return a == b
            case (Err(a), Err(b)):
                return a == b
            case _:
                return False

    def __or__[U](self, mapper: Callable[[T], "Result[U, E]"]) -> "Result[U, E]" | Self:
        return self.and_then(mapper)


@dataclass
class Ok[T](_Result[T, Any]):
    value: T

    def __repr__(self) -> str:
        return f"Ok({self.value!r})"


@dataclass
class Err[E](_Result[Any, E]):
    value: E

    def __repr__(self) -> str:
        return f"Err({self.value!r})"


type Result[T, E] = Ok[T] | Err[E]


def catch[**P, T](func: Callable[P, Result[T, Exception]]) -> Callable[P, Result[T, Exception]]:
    """
    Catch all exceptions and return an Err of the exception

    >>> @catch
    ... def divide(a: float, b: float) -> Result[float, Exception]:
    ...     return Ok(a / b)
    >>> divide(10, 2)
    Ok(5.0)
    >>> divide(10, 0)
    Err(ZeroDivisionError('division by zero'))
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[T, Exception]:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return Err(e)

    return wrapper


def catch_repr[**P, T](
    func: Callable[P, Result[T, str]],
) -> Callable[P, Result[T, str]]:
    """
    Catch all exceptions and return an Err of the exception's __repr__

    >>> @catch_repr
    ... def divide(a: float, b: float) -> Result[float, str]:
    ...     return Ok(a / b)
    >>> divide(10, 2)
    Ok(5.0)
    >>> divide(10, 0)
    Err("ZeroDivisionError('division by zero')")
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[T, str]:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return Err(e.__repr__())

    return wrapper


def catch_msg[**P, T](
    func: Callable[P, Result[T, str]],
) -> Callable[P, Result[T, str]]:
    """
    Catch all exceptions and return an Err of the exception's __str__

    >>> @catch_msg
    ... def divide(a: float, b: float) -> Result[float, str]:
    ...     return Ok(a / b)
    >>> divide(10, 2)
    Ok(5.0)
    >>> divide(10, 0)
    Err('division by zero')
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[T, str]:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return Err(str(e))

    return wrapper


def catch_map[**P, T, E](
    exception_type: type[Exception] | tuple[type[Exception], ...],
    mapper: Callable[[Exception], Result[T, E]],
) -> Callable[[Callable[P, Result[T, E]]], Callable[P, Result[T, E]]]:
    """
    Catch excpetions of specified types and map them to an Err of the mapped type

    >>> @catch_map((TypeError, ValueError), lambda _: Err("Invalid input"))
    ... @catch_map(ZeroDivisionError, lambda _: Err("Division by zero"))
    ... def divide(a: float, b: float) -> Result[float, str]:
    ...     return Ok(a / b)
    >>> divide(10, 2)
    Ok(5.0)
    >>> divide(10, 0)
    Err('Division by zero')
    >>> divide("hello", 0)
    Err('Invalid input')
    """

    def decorator(func: Callable[P, Result[T, E]]) -> Callable[P, Result[T, E]]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[T, E]:
            try:
                result = func(*args, **kwargs)
                return result
            except exception_type as e:
                return mapper(e)

        return wrapper

    return decorator
