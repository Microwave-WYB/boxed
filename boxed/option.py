from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from re import T
from typing import Optional

from boxed.error import UnwrapError


class _Option[T]:
    def __init__(self, value: Optional[T]) -> None:
        self.value = value

    def unwrap(self) -> T:
        """
        >>> Some(1).unwrap()
        1
        >>> Null().unwrap()
        Traceback (most recent call last):
            ...
        boxed.error.UnwrapError
        """
        if self.value is None:
            raise UnwrapError
        return self.value

    def unwrap_or(self, default: T, /) -> T:
        """
        >>> Some(1).unwrap_or(2)
        1
        >>> Null().unwrap_or(2)
        2
        """
        if self.value is None:
            return default
        return self.value

    def unwrap_or_else(self, f: Callable[[], T], /) -> T:
        """
        >>> Some(1).unwrap_or_else(lambda: 2)
        1
        >>> Null().unwrap_or_else(lambda: 2)
        2
        """
        if self.value is None:
            return f()
        return self.value

    def expect(self, msg: str, /) -> T:
        """
        >>> Some(1).expect("Error")
        1
        >>> Null().expect("Error")
        Traceback (most recent call last):
            ...
        boxed.error.UnwrapError: Error
        """
        if self.value is None:
            raise UnwrapError(msg)
        return self.value

    def is_some(self) -> bool:
        """
        >>> Some(1).is_some()
        True
        >>> Null().is_some()
        False
        """
        return self.value is not None

    def is_none(self) -> bool:
        """
        >>> Some(1).is_none()
        False
        >>> Null().is_none()
        True
        """
        return self.value is None

    def map(self, mapper: Callable[[T], T], /) -> "_Option[T]":
        """
        >>> Some(1).map(lambda x: x + 1)
        Some(2)
        >>> Null().map(lambda x: x + 1)
        Null()
        """
        if self.value is None:
            return Null()
        return Some(mapper(self.value))

    def and_then[U](self, mapper: Callable[[T], "_Option[U]"], /) -> "_Option[U]":
        """
        >>> Some(1).and_then(lambda x: Some(x + 1))
        Some(2)
        >>> Some(1).and_then(lambda x: Null())
        Null()
        """
        if self.value is None:
            return Null()
        return mapper(self.value)

    def or_(self, optb: "_Option[T]", /) -> "_Option[T]":
        """
        >>> Some(1).or_(Some(2))
        Some(1)
        >>> Some(1).or_(Null())
        Some(1)
        >>> Null().or_(Some(2))
        Some(2)
        >>> Null().or_(Null())
        Null()
        """
        if self.value is None:
            return optb
        return self

    def or_else(self, f: Callable[[], "_Option[T]"], /) -> "_Option[T]":
        """
        >>> Some(1).or_else(lambda: Null())
        Some(1)
        >>> Null().or_else(lambda: Some(2))
        Some(2)
        """
        if self.value is None:
            return f()
        return self

    def __bool__(self) -> bool:
        return self.is_some()

    def __eq__(self, other: object, /) -> bool:
        if self.value is None:
            return other is None
        return self.value == other

    def __repr__(self) -> str:
        if self.value is None:
            return "Null()"
        return f"Some({self.value!r})"

    def __or__(self, optb: "_Option[T]", /) -> "_Option[T]":
        return self.or_(optb)

    def __rshift__[U](self, mapper: Callable[[T], "_Option[U]"], /) -> "_Option[U]":
        return self.and_then(mapper)


@dataclass
class Some[T](_Option[T]):
    value: T

    def __repr__(self) -> str:
        return f"Some({self.value!r})"


class Null[T: None](_Option[T]):
    def __init__(self) -> None:
        super().__init__(None)

    def __repr__(self) -> str:
        return "Null()"


type Option[T] = Some[T] | Null[None]


def as_option[T](value: Optional[T]) -> Option[T]:
    if value is None:
        return Null()
    return Some(value)


def option[**P, T](f: Callable[P, Optional[T]]) -> Callable[P, Option[T]]:
    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Option[T]:
        value = f(*args, **kwargs)
        return as_option(value)

    return wrapper
