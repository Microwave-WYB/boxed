import random

from boxed.ordering import Ordering, cmp
from boxed.result import Err, Ok, Result


def get_input() -> Result[str, str]:
    try:
        return Ok(input("Enter your guess: "))
    except Exception:
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
    number = random.randint(1, 100)

    while True:
        match get_input().and_then(parse_guess):
            case Ok(guess):
                match cmp(guess, number):
                    case Ordering.Equal:
                        print("Congratulations! You guessed the number!")
                        return
                    case Ordering.Less:
                        print("Too low. Try again.")
                    case Ordering.Greater:
                        print("Too high. Try again.")
            case Err(msg):
                print(msg)


if __name__ == "__main__":
    play_game()
