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
