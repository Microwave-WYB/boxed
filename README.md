# Boxed Library

Boxed is a Python library that brings Rust-like `Option` and `Result` types to Python, along with pattern matching capabilities. This library is designed for Python developers who are already familiar with Rust concepts and want to apply similar patterns in their Python code.

## Features

- Rust-like `Option` type
- Rust-like `Result` type
- Pattern matching using Python's `match` statement
- Ordering comparisons

## Installation

This library strongly rely on Python 3.12's generic typing syntax. Make sure you have Python 3.12+

To install the library, run

```bash
pip install boxed
```

## Usage

### Option

The `Option` type represents an optional value: every `Option` is either `Some` and contains a value, or `Null` and does not.

```python
from boxed.option import Some, Null, Option

# Creating Options
some_value = Some(42)
no_value = Null()

# Working with Options
def divide(a: int, b: int) -> Option[float]:
    match b:
        case 0:
            return Null()
        case _:
            return Some(a / b)

result = divide(10, 2)  # Some(5.0)
result = divide(10, 0)  # Null()

# Pattern matching
match result:
    case Some(value):
        print(f"Result: {value}")
    case Null():
        print("Division by zero")

# Using Option methods
print(some_value.unwrap())  # 42
print(no_value.unwrap_or(0))  # 0
print(some_value.map(lambda x: x * 2).unwrap())  # 84
```

### Result

The `Result` type is used for returning and propagating errors. It has two variants: `Ok`, representing success and containing a value, and `Err`, representing error and containing an error value.

```python
from boxed.result import Ok, Err, Result

# Creating Results
success = Ok(42)
error = Err("Something went wrong")

# Working with Results
def safe_divide(a: int, b: int) -> Result[float, str]:
    if b == 0:
        return Err("Cannot divide by zero")
    return Ok(a / b)

result = safe_divide(10, 2)  # Ok(5.0)
result = safe_divide(10, 0)  # Err("Cannot divide by zero")

# Pattern matching
match result:
    case Ok(value):
        print(f"Result: {value}")
    case Err(error):
        print(f"Error: {error}")

# Using Result methods
print(success.unwrap())  # 42
print(error.unwrap_or(0))  # 0
print(success.map(lambda x: x * 2).unwrap())  # 84
```

### Ordering

The `Ordering` type is used for comparison results.

```python
from boxed.ordering import Ordering, cmp

# Comparing values
order = cmp(5, 10)  # Ordering.Less
order = cmp(10, 5)  # Ordering.Greater
order = cmp(5, 5)   # Ordering.Equal

# Pattern matching
match order:
    case Ordering.Less:
        print("Less")
    case Ordering.Greater:
        print("Greater")
    case Ordering.Equal:
        print("Equal")
```

## Examples

### Guessing Game

```python
import random

from boxed.ordering import Ordering, cmp
from boxed.result import Err, Ok, Result


def get_input() -> Result[str, str]:
    try:
        return Ok(input("Enter your guess: "))
    except EOFError:
        return Err("Unexpected end of input.")


def parse_guess(input_str: str) -> Result[int, str]:
    try:
        num = int(input_str)
        if 1 <= num <= 100:
            return Ok(num)
        else:
            return Err("Please enter a number between 1 and 100.")
    except ValueError:
        return Err("Invalid input. Please enter a number.")


def play_game() -> None:
    secret_number = random.randint(1, 100)
    print("Welcome to the Guess the Number game!")
    print("I'm thinking of a number between 1 and 100.")

    while True:
        match get_input().and_then(parse_guess):
            case Ok(guess):
                match cmp(guess, secret_number):
                    case Ordering.Less:
                        print("Too low. Try again.")
                    case Ordering.Greater:
                        print("Too high. Try again.")
                    case Ordering.Equal:
                        print("Congratulations! You guessed the number!")
                        return
            case Err(msg):
                print(msg)


if __name__ == "__main__":
    play_game()

```

### BLE Advertisement Parser

```python
from collections.abc import Iterator
from dataclasses import dataclass

from boxed.result import Err, Ok, Result


@dataclass(frozen=True)
class AdStruct:
    data_type: int
    data: bytes


def parse_next(data: bytes) -> Result[tuple[AdStruct, bytes], str]:
    match list(data):
        case [l, t, *d]:
            return Ok((AdStruct(t, bytes(d[:l])), bytes(d[l:])))
        case _:
            return Err("Invalid data format.")


def ad_structs(data: bytes) -> Iterator[AdStruct]:
    match data:
        case b"":
            return
        case _:
            ad, rest = parse_next(data).unwrap()
            yield ad
            yield from ad_structs(rest)


if __name__ == "__main__":
    data = bytes(
        [0x02, 0x01, 0x06]
        + [
            0x06,
            0xFF,
            0x01,
            0x02,
            0x03,
            0x04,
            0x05,
        ]
    )
    for ad in ad_structs(data):
        print(ad)

```

## Why use Boxed?

Boxed brings Rust-like error handling and optional value management to Python, allowing for more expressive and safer code. It's particularly useful for developers who appreciate Rust's approach to these concepts and want to apply similar patterns in their Python projects.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
