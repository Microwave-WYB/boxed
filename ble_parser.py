from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(frozen=True)
class AdStruct:
    data_type: int
    data: bytes


def ad_structs(data: bytes) -> Iterator[AdStruct]:
    match list(data):
        case []:
            return
        case [l, t, *d]:
            yield AdStruct(t, bytes(d[: l - 1]))
            yield from ad_structs(bytes(d[l - 1 :]))
        case _:
            raise ValueError("Invalid data format.")


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
