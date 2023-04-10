table2md
========

Print tabular data in markdown format

Installation
------------

Tested on Pythons above 3.6+.
`pip3 install table2md`

Usage
-----

```py
from table2md import MarkdownTable

# All following examples print the following table onto stdout:
# | constant | value |
# |----------|-------|
# | e        | 2.71  |
# | pi       | 3.14  |
# | sqrt2    | 1.41  |

# With dictionaries
MarkdownTable.from_dicts([
    {"constant": "e", "value": 2.71},
    {"constant": "pi", "value": 3.14},
    {"constant": "sqrt2", "value": 1.41},
]).print()

# With 2D iterables
MarkdownTable.from_2d_iterable([
    ["constant", "value"],
    ["pi", 6.28],
    ["e", 2.71],
    ["sqrt2", 1.41],
]).print()

# With named tuples
from typing import NamedTuple

class Constant(NamedTuple):
    constant: str
    value: float

MarkdownTable.from_namedtuples([
    Constant("e", 2.71),
    Constant("pi", 3.14),
    Constant("sqrt2", 1.41),
]).print()
```

MarkdownTable automatically coalesces all values into strings (with `str(value)`);
with the exception of the `MarkdownTable.from_dicts`, where keys are assumed to be strings.

To use custom formatting, either coalesce values into strings on your own,
use your own classes with custom `__str__` methods,
or use the special `MarkdownTable.from_serializable` constructor.

It takes an iterable of objects with `_fields` property and a `serialize` method. Example:

```py
from table2md import MarkdownTable
from typing import NamedTuple
from datetime import datetime

# Named tuples already provide the _fields property,
# so we only need to implement the serialize method.
class TemperatureReadout(NamedTuple):
    tstamp: datetime
    value: float

    def serialize(self) -> tuple[str, str]:
        return self.tstamp.strftime("%Y-%m-%d %H:%M"), f"{self.value:.1f}"

MarkdownTable.from_serializable([
    TemperatureReadout(datetime(2021, 11, 1, 10, 0, 0), 10.411),
    TemperatureReadout(datetime(2021, 11, 1, 12, 0, 0), 12.782),
    TemperatureReadout(datetime(2021, 11, 1, 14, 0, 0), 11.214),
]).print()
# Output:
# |      tstamp      | value |
# |------------------|-------|
# | 2021-11-01 10:00 | 10.4  |
# | 2021-11-01 12:00 | 12.8  |
# | 2021-11-01 14:00 | 11.2  |
```

Documentation
-------------

#### MarkdownTable

A class to represent tabular data

- **MarkdownTable(data: List[List[Str]])**:  
    Initializes a table from a 2D list of strings.
    1st row is always the header row.
    See utility MarkdownTable.from_* helper classmethods.
    Provided lists are not copied!

- **markdown_table.\_\_str\_\_() -> str**:  
    Serializes the contained tabular data to a markdown table.
    First row is assumed to be the header row.

- **markdown_table.validate() -> None**:  
    Ensures the contained table is good-to-print -
    that is it has a header; and all rows with data have the same number
    of cells as the header.  
    Raises a sub-class of InvalidData in case invalid state is detected.

- **markdown_table.print(end: str = "", file: SupportsWrite[str] = sys.stdout, flush: bool = False) -> None**:  
    Validates the table, and then prints it.
    'end', 'file' and 'flush' arguments are passed
    through to the builtin print function.  
    Pleas note that the serialized table already has a newline at the end,
    so `end="\n"` is not necessary.

- **markdown_table.display() -> None**:  
    Validates the table, then tries to pretty-print
    using IPython.display.display_markdown.

    If that is not available, the same as table.print()

- **MarkdownTable.from_2d_iterable(iters: Iterable[Iterable[Any]]) -> MarkdownTable**:  
    Initializes the table from a 2D iterable.
    Every cell is saved by calling `str(cell)`.
    If provided with a 2D list, those lists are copied
    (this is different to the behavior from the constructor).

- **MarkdownTable.from_dicts(dicts: Iterable[Mapping[str, Any]]) -> MarkdownTable:**:  
    Initializes the table from an iterable of dictionaries.
    Every value is saved by calling `str(cell)`.  
    Only keys from the first dictionary are used; that is any extra key
    in other dictionaries are ignored.
    However, if a following dict has a missing key, KeyError is thrown.

- **MarkdownTable.from_namedtuples(named_tuples: Iterable[_NamedTupleLike]) -> MarkdownTable**:  
    Initializes the table from an iterable of NamedTuples.  
    Well, in reality those don't have to be NamedTuples per se;
    as longs at the objects have a `_fields` property
    and one can iterate over those objects this function works fine.  
    First object's `_fields` property is the header row.  
    If objects aren't of the same type, ensure all of them have the same amount of fields;
    otherwise an invalid table is created.

- **MarkdownTable.from_serializable(objects: Iterable[_Serializable]) -> MarkdownTable**:  
    This is an extension of from_namedtuples; but instead of iterating over
    those objects directly, obj.serialize() is used to get the string representations
    of the cells.  
    So, as long as objects have the `_fields` property and
    a `serialize()` method; this method works fine.  
    First object's `_fields` property is the header row.  
    Ensure all object's serialize() method yield the same amount of cells,
    otherwise an invalid table is created.

#### Exceptions

- **InvalidData**:
    Base exception fort use in table validation. Subclasses `ValueError`.

- **NoData**:
    Exception used when a table has absolutely no data; not even a header row.
    Subclasses `InvalidData`.

- **MisalignedRows**:
    Exception used when a table has rows with more/less cells than the header.
    Subclasses `InvalidData`.

#### Protocols/Interfaces

- **SupportsWrite[str]**:
    Anything with a write method accepting a string argument.
    [Implemented by the _typeshed module](https://github.com/python/typeshed/blob/master/stdlib/_typeshed/__init__.pyi#L173).

- **_NamedTupleLike**:
    Anything with a `_fields` property, which is an iterable of strings
    representing field names; that is itself iterable.

- **_Serializable**:
    Anything with a `_fields` property, which is an iterable of strings
    representing field names; and with a `serialize() -> Iterable[str]` method
    which returns all the held field values as strings.
