# © Copyright 2021 Mikołaj Kuranowski
# SPDX-License-Identifier: MIT

import sys
from typing import TYPE_CHECKING, Any, Iterable, Iterator, List, Mapping, Type, TypeVar

if sys.version_info < (3, 8):
    from typing_extensions import Protocol
else:
    from typing import Protocol

if TYPE_CHECKING:
    from _typeshed import SupportsWrite


__title__ = "table2md"
__description__ = "Print tabular data in markdown format"
__version__ = "0.0.1"
__url__ = "https://github.com/MKuranowski/table2md"
__author__ = "Mikołaj Kuranowski"
__email__ = "mkuranowski+pypackages@gmail.com"

__copyright__ = "© Copyright 2021 Mikołaj Kuranowski"
__license__ = "MIT"


class _NamedTupleLike(Protocol):
    """_NamedTupleLike describes the interface accepted by
    MarkdownTable.from_namedtuples.

    This interface is always implemented by collections.namedtuple
    types, hence the name.
    """
    @property
    def _fields(self) -> Iterable[str]: ...
    def __iter__(self) -> Iterator[Any]: ...


class _Serializable(Protocol):
    """_Seralizable describes the interface accepted by
    MarkdownTable.from_seralizable.

    This interface was designed to allow custom to-string conversion
    without having to create custom types with custom __str__ methods.

    The easiest way to implement this interface is by subclassing typing.NamedTuple
    and providing a `serialize` method.
    """
    @property
    def _fields(self) -> Iterable[str]: ...
    def serialize(self) -> Iterable[str]: ...


class InvalidData(ValueError):
    """Base exception fort use in table validation"""
    pass


class NoData(InvalidData):
    """Exception used when a table has absolutely no data; not even a header row"""
    pass


class MisalignedRows(InvalidData):
    """Exception used when a table has rows with more/less cells than the header"""
    pass


class MarkdownTable:
    """A class to represent tabular data"""

    def __init__(self, data: List[List[str]]):
        """Initializes a table from a 2D list of strings.
        1st row is always the header row.
        See utility MarkdownTable.froListm_* helper classmethods.
        Provided lists are not copied!
        """
        self.data: List[List[str]] = data

    def __str__(self) -> str:
        """Serializes the contained tabular data to a markdown table.
        First row is assumed to be the header row.
        """
        x = ""

        # First, pre-calculate column sizes
        col_sizes: List[int] = [
            max(len(cell) for cell in col)
            for col in zip(*self.data)
        ]

        # Add the header
        x += "|"
        x += "|".join(cell.center(col_sizes[col_idx] + 2)
                      for col_idx, cell in enumerate(self.data[0]))
        x += "|\n"

        # Add the header separator
        x += "|"
        x += "|".join("-" * (col_size + 2) for col_size in col_sizes)
        x += "|\n"

        # Add data rows
        for row in self.data[1:]:
            x += "| "
            x += " | ".join(cell.ljust(col_sizes[col_idx]) for col_idx, cell in enumerate(row))
            x += " |\n"

        return x

    def validate(self) -> None:
        """Ensures the contained table is good-to-print -
        that is it has a header; and all rows with data have the same number
        of cells as the header.

        Raises a sub-class of InvalidData.
        """
        if not self.data:
            raise NoData("missing header row")
        elif len(self.data) == 1:
            raise NoData("only the header is present")
        header_len = len(self.data[0])
        invalid_rows = [idx for (idx, row) in enumerate(self.data[1:], 1)
                        if len(row) != header_len]
        if invalid_rows:
            raise MisalignedRows(f"expected {header_len} cells, violated by rows "
                                 + ", ".join(map(str, invalid_rows)))

    def print(self, end: str = "", file: "SupportsWrite[str]" = sys.stdout,
              flush: bool = False) -> None:
        """Validates the table, and then prints it.
        'end', 'file' and 'flush' arguments are passed
        through to the builtin print function.

        Pleas note that the serialized table already has a newline at the end,
        so `end="\n"` is not neccessary.
        """
        self.validate()
        print(str(self), end=end, file=file, flush=flush)

    @classmethod
    def from_2d_iterable(cls, iters: Iterable[Iterable[Any]]) -> "MarkdownTable":
        """Initializes the table from a 2D iterable.
        Every cell is saved by calling `str(cell)`.
        If provided with a 2D list, those lists are copied
        (this is different to the behavior from the constructor).
        """
        return cls([[str(cell) for cell in row] for row in iters])

    @classmethod
    def from_dicts(cls, dicts: Iterable[Mapping[str, Any]]) -> "MarkdownTable":
        """Initializes the table from an iterable of dictionaries.
        Every value is saved by calling `str(cell)`.

        Only keys from the first dictionary are used; that is any extra key
        in other dictionaries are ignored.
        However, if a following dict has a missing key, KeyError is thrown.
        """
        data: List[List[str]] = []

        for d in dicts:
            # No header
            if not data:
                data.append([k for k in d.keys()])
            data.append([str(d[k]) for k in data[0]])

        return cls(data)

    @classmethod
    def from_namedtuples(cls, named_tuples: Iterable[_NamedTupleLike]) -> "MarkdownTable":
        """Initializes the table from an iterable of NamedTuples.

        Well, in reality those don't have to be NamedTuples per se;
        as longs at the objects have a `_fields` property
        and one can iterate over those objects this function works fine.

        First object's `_fields` property is the header row.

        If objects aren't of the same type, ensure all of them have the same amount of fields;
        otherwise an invalid table is created.
        """
        data: List[List[str]] = []

        for nt in named_tuples:
            # No header
            if not data:
                data.append(list(nt._fields))
            data.append([str(i) for i in nt])

        return cls(data)

    @classmethod
    def from_serializable(cls, named_tuples: Iterable[_Serializable]) -> "MarkdownTable":
        """This is an extension of from_namedtuples; but instead of iterating over
        those objects directly, obj.serialize() is used to get the string representations
        of the cells.

        So, as long as objects have the `_fields` property and
        a `serialize()` method; this method works fine.

        First object's `_fields` property is the header row.

        Ensure all object's serialize() method yield the same amount of cells,
        otherwise an invalid table is created.
        """
        data: List[List[str]] = []

        for nt in named_tuples:
            # No header
            if not data:
                data.append(list(nt._fields))
            data.append(list(nt.serialize()))

        return cls(data)
