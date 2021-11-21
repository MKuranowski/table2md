# © Copyright 2021 Mikołaj Kuranowski
# SPDX-License-Identifier: MIT

from typing import NamedTuple, Tuple
from table2md import MarkdownTable, MisalignedRows, NoData
from io import StringIO
import pytest


class Measurement(NamedTuple):
    name: str
    percentage: float

    def serialize(self) -> Tuple[str, str]:
        return self.name, f"{self.percentage:.1%}"


class EnhancesMeasurement(NamedTuple):
    name: str
    percentage: float
    serial_no: int

    def serialize(self) -> Tuple[str, str, str]:
        return self.name, f"{self.percentage:.1%}", f"{self.serial_no:0>3}"


def test_init_simple():
    f = StringIO()
    MarkdownTable([["foo", "bar"], ["spam", "eggs"], ["hello", "world"]]).print(file=f)
    assert f.getvalue() == \
        "|  foo  |  bar  |\n" \
        "|-------|-------|\n" \
        "| spam  | eggs  |\n" \
        "| hello | world |\n"


def test_init_no_copy():
    f = StringIO()
    data = [["constant", "value"], ["pi", "6.28"], ["e", "2.71"]]
    t = MarkdownTable(data)
    data[1][0] = "tau"
    t.print(file=f)
    assert f.getvalue() == \
        "| constant | value |\n" \
        "|----------|-------|\n" \
        "| tau      | 6.28  |\n" \
        "| e        | 2.71  |\n"


def test_validate_ok():
    MarkdownTable([["constant", "value"], ["pi", "6.28"], ["e", "2.71"]]).validate()


def test_validate_nothing():
    with pytest.raises(NoData):
        MarkdownTable([]).validate()


def test_validate_header_only():
    with pytest.raises(NoData):
        MarkdownTable([["constant", "value"]]).validate()


def test_validate_misaligned_rows():
    with pytest.raises(MisalignedRows):
        MarkdownTable([["constant", "value"], ["pi", "6.28"], ["e"]]).validate()


def test_from_2d_iterable():
    f = StringIO()
    MarkdownTable.from_2d_iterable(range(i * 3, i * 3 + 3) for i in range(3)).print(file=f)
    assert f.getvalue() == \
        "| 0 | 1 | 2 |\n" \
        "|---|---|---|\n" \
        "| 3 | 4 | 5 |\n" \
        "| 6 | 7 | 8 |\n"


def test_from_2d_iterable_copies():
    f = StringIO()
    data = [["constant", "value"], ["pi", "6.28"], ["e", "2.71"]]
    t = MarkdownTable.from_2d_iterable(data)
    data[1][0] = "tau"
    t.print(file=f)
    assert f.getvalue() == \
        "| constant | value |\n" \
        "|----------|-------|\n" \
        "| pi       | 6.28  |\n" \
        "| e        | 2.71  |\n"


def test_from_dicts():
    f = StringIO()
    MarkdownTable.from_dicts([
        {"constant": "e", "value": 2.71},
        {"constant": "pi", "value": 3.14},
        {"constant": "sqrt2", "value": 1.41},
    ]).print(file=f)

    assert f.getvalue() == \
        "| constant | value |\n" \
        "|----------|-------|\n" \
        "| e        | 2.71  |\n" \
        "| pi       | 3.14  |\n" \
        "| sqrt2    | 1.41  |\n"


def test_from_dicts_ingores_additional_keys():
    f = StringIO()
    MarkdownTable.from_dicts([
        {"constant": "e", "value": 2.71},
        {"constant": "pi", "value": 3.14, "alt_name": "half tau"},
        {"constant": "sqrt2", "value": 1.41, "alt_name": "square root of 2"},
    ]).print(file=f)

    assert f.getvalue() == \
        "| constant | value |\n" \
        "|----------|-------|\n" \
        "| e        | 2.71  |\n" \
        "| pi       | 3.14  |\n" \
        "| sqrt2    | 1.41  |\n"


def test_from_dicts_key_error_on_missing_key():
    with pytest.raises(KeyError):
        MarkdownTable.from_dicts([
            {"constant": "e", "value": 2.71},
            {"constant": "pi", "value": 3.14},
            {"constant": "sqrt2"},
        ])


def test_from_namedtuple():
    f = StringIO()
    MarkdownTable.from_namedtuples([
        Measurement("foo", 0.253),
        Measurement("bar", 0.2137),
        Measurement("baz", 0.111),
    ]).print(file=f)

    assert f.getvalue() == \
        "| name | percentage |\n" \
        "|------|------------|\n" \
        "| foo  | 0.253      |\n" \
        "| bar  | 0.2137     |\n" \
        "| baz  | 0.111      |\n"


def test_from_namedtuple_misaligned():
    # NOTE: This both type-checks and doesn't throw an error!
    t = MarkdownTable.from_namedtuples([
        Measurement("foo", 0.253),
        Measurement("bar", 0.2137),
        EnhancesMeasurement("baz", 0.111, 69),
    ])

    with pytest.raises(MisalignedRows):
        t.validate()


def test_from_serializable():
    f = StringIO()
    MarkdownTable.from_serializable([
        Measurement("foo", 0.253),
        Measurement("bar", 0.2137),
        Measurement("baz", 0.111),
    ]).print(file=f)

    assert f.getvalue() == \
        "| name | percentage |\n" \
        "|------|------------|\n" \
        "| foo  | 25.3%      |\n" \
        "| bar  | 21.4%      |\n" \
        "| baz  | 11.1%      |\n"


def test_from_serializable_misaligned():
    # NOTE: This both type-checks and doesn't throw an error!
    t = MarkdownTable.from_serializable([
        Measurement("foo", 0.253),
        Measurement("bar", 0.2137),
        EnhancesMeasurement("baz", 0.111, 69),
    ])

    with pytest.raises(MisalignedRows):
        t.validate()
