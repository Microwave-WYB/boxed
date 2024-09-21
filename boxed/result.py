from abc import ABC
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any, Self

from boxed.error import UnwrapError


class _Result[T, E](ABC):
    def __init__(self, value: T, error: E) -> None:
        self.value = value
        self.error = error

    def unwrap(self) -> T:
        """
        >>> Ok(1).unwrap()
        1
        >>> Err("Error").unwrap()
        Traceback (most recent call last):
            ...
        boxed.error.UnwrapError: Error
        """
        if self.error is not None:
            raise UnwrapError(self.error)
        return self.value

    def expect(self, msg: str) -> T:
        """
        >>> Ok(1).expect("Error")
        1
        >>> Err("Error").expect("Error")
        Traceback (most recent call last):
            ...
        boxed.error.UnwrapError: Error
        """
        if self.error is not None:
            raise UnwrapError(msg)
        return self.value

    def unwrap_or(self, default: T) -> T:
        """
        >>> Ok(1).unwrap_or(2)
        1
        >>> Err("Error").unwrap_or(2)
        2
        """
        if self.error is not None:
            return default
        return self.value

    def unwrap_or_else(self, default: Callable[[], T]) -> T:
        """
        >>> Ok(1).unwrap_or_else(lambda: 2)
        1
        >>> Err("Error").unwrap_or_else(lambda: 2)
        2
        """
        if self.error is not None:
            return default()
        return self.value

    def is_ok(self) -> bool:
        """
        >>> Ok(1).is_ok()
        True
        >>> Err("Error").is_ok()
        False
        """
        return self.error is None

    def is_err(self) -> bool:
        """
        >>> Ok(1).is_err()
        False
        >>> Err("Error").is_err()
        True
        """
        return self.error is not None

    def map(self, mapper: Callable[[T], T]) -> "_Result[T, E]":
        """
        >>> Ok(1).map(lambda x: x + 1)
        Ok(value=2)
        >>> Err("Error").map(lambda x: x + 1)
        Err(error='Error')
        """
        if self.error is not None:
            return self
        return Ok(mapper(self.value))

    def map_err(self, mapper: Callable[[E], E]) -> "_Result[T, E]":
        """
        >>> Ok(1).map_err(lambda x: x + 1)
        Ok(value=1)
        >>> Err("Error").map_err(lambda x: x.upper())
        Err(error='ERROR')
        """
        if self.error is not None:
            return Err(mapper(self.error))
        return self

    def and_then[U](self, mapper: Callable[[T], "_Result[U, E]"]) -> "_Result[U, E]" | Self:
        """
        >>> Ok(1).and_then(lambda x: Ok(x + 1))
        Ok(value=2)
        >>> Ok(1).and_then(lambda x: Err("Error"))
        Err(error='Error')
        >>> Err("Error").and_then(lambda x: Ok(x + 1))
        Err(error='Error')
        """
        if self.error is not None:
            return self
        return mapper(self.value)

    def __bool__(self) -> bool:
        return self.is_ok()

    def __eq__(self, other: object) -> bool:
        """
        >>> Ok(1) == Ok(1)
        True
        >>> Err("Error") == Err("Error")
        True
        >>> Err("Error") == Ok(1)
        False
        """
        if not isinstance(other, _Result):
            return NotImplemented
        return self.value == other.value and self.error == other.error

    def __or__(self, other: T) -> T:
        return self.unwrap_or(other)

    def __rshift__[U](self, mapper: Callable[[T], "_Result[U, E]"]) -> "_Result[U, E]" | Self:
        return self.and_then(mapper)


@dataclass
class Ok[T](_Result[T, Any]):
    value: T

    def __init__(self, value: T, /) -> None:
        super().__init__(value, None)


@dataclass
class Err[T](_Result[Any, T]):
    error: T

    def __init__(self, error: T, /) -> None:
        super().__init__(None, error)


type Result[T_Ok, T_Err] = Ok[T_Ok] | Err[T_Err]


def catch[**P, T, E: Exception](
    *exceptions: type[E],
) -> Callable[[Callable[P, Result[T, str]]], Callable[P, Result[T, str]]]:
    def decorator(func: Callable[P, Result[T, str]]) -> Callable[P, Result[T, str]]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[T, str]:
            try:
                result = func(*args, **kwargs)
                match result:
                    case Ok(_) | Err(_):
                        return result
                    case _:
                        return Ok(result)
            except exceptions as e:
                return Err(str(e))

        return wrapper

    return decorator
