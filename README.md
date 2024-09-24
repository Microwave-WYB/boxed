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
# pip install boxed  # this will not work at the moment
pip install git+https://github.com/Microwave-WYB/boxed.git
```

## Usage

### Option

The `Option` type in this library provides a safe and expressive way to handle potentially absent values in Python. It's an implementation of the Option monad, a concept from functional programming that helps eliminate null pointer exceptions and makes code more readable.

#### Creating Options

```python
from boxed.option import Some, Null, Option

# For a present value
some_value = Some(42)

# For an absent value
no_value = Null

# Create from a value that might be None
maybe_value = Option.from_(some_function_that_might_return_none())
```

#### Basic Usage with `match`

```python
value = some_function_that_might_return_none()
match value:
    case Some(v):
        v.do_something
    case Null:
        print("skipping")
```

#### Unwrapping Values

```python
# Get the value or raise an UnwrapError if Null
value = some_value.unwrap()

# Get the value or return a default if Null
value = no_value.unwrap_or(0)

# Get the value or compute a default if Null
value = no_value.unwrap_or_else(lambda: compute_default())
```

#### Checking State

```python
if some_value.is_some():
    print("Value is present")

if no_value.is_none():
    print("Value is absent")
```

#### Transforming Options

```python
# Apply a function to the value if present
doubled = some_value.map(lambda x: x * 2)

# Chain operations that return Options
result = some_value.and_then(lambda x: Some(x) if x > 0 else Null)
```

#### Combining Options

```python
# Return the first non-Null Option
result = no_value.or_(Some(42))

# Compute an alternative Option if Null
result = no_value.or_else(lambda: Some(compute_alternative()))
```

#### Using the Option Decorator

The `@option` decorator can be used to convert functions that return `Optional[T]` to functions that return `Option[T]`:

```python
from boxed import option

@option
def parse_int(s: str) -> Optional[int]:
    return int(s) if s.isdigit() else None

result = parse_int("123")  # Returns Some(123)
result = parse_int("abc")  # Returns Null
```

By using `Option`, you can write more expressive and safer code, reducing the risk of attribute errors when calling optional objects.
