from abc import ABC
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any, Self

from boxed.error import UnwrapError


class _Result[T_Ok, T_Err](ABC):
    def __init__(self, value: T_Ok, error: T_Err) -> None:
        self.value = value
        self.error = error

    def unwrap(self) -> T_Ok:
        if self.error is not None:
            raise UnwrapError(self.error)
        return self.value

    def expect(self, msg: str) -> T_Ok:
        if self.error is not None:
            raise UnwrapError(msg)
        return self.value

    def unwrap_or(self, default: T_Ok) -> T_Ok:
        if self.error is not None:
            return default
        return self.value

    def unwrap_or_else(self, default: Callable[[], T_Ok]) -> T_Ok:
        if self.error is not None:
            return default()
        return self.value

    def is_ok(self) -> bool:
        return self.error is None

    def is_err(self) -> bool:
        return self.error is not None

    def map(self, mapper: Callable[[T_Ok], T_Ok]) -> "_Result[T_Ok, T_Err]":
        if self.error is not None:
            return self
        return Ok(mapper(self.value))

    def map_err(self, mapper: Callable[[T_Err], T_Err]) -> "_Result[T_Ok, T_Err]":
        if self.error is not None:
            return Err(mapper(self.error))
        return self

    def and_then[T_Ok2, T_Err2](
        self, mapper: Callable[[T_Ok], "_Result[T_Ok2, T_Err2]"]
    ) -> "_Result[T_Ok2, T_Err2]" | Self:
        if self.error is not None:
            return self
        return mapper(self.value)


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


def catch[**P, T, E: Exception](*exceptions: type[E]):
    def decorator(func: Callable[P, Result[T, E]]) -> Callable[P, Result[T, E]]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[T, E]:
            try:
                result = func(*args, **kwargs)
                match result:
                    case Ok(_) | Err(_):
                        return result
                    case _:
                        return Ok(result)
            except exceptions as e:
                return Err(e)

        return wrapper

    return decorator
