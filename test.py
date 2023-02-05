from __future__ import annotations

import os
import sys
import tempfile
import traceback
from typing import List

import yaml

import muconf as mcf

_TEST_F = []


def test(f):
    _TEST_F.append(f)
    return f


@test
def test_load_from_file():
    @mcf.config(isroot=True)
    class TestConf:
        foo: int = 1
        bar: str = "hello"
        baz: float
        bam: list[int] = None
        fang = 6

    with tempfile.TemporaryDirectory() as tmpd:
        conf_path = os.path.join(tmpd, "test_conf.yaml")
        test_conf = {"baz": 0.9, "fang": 10}
        with open(conf_path, "w+") as f:
            f.write(yaml.dump(test_conf))
        mcf.load_from_file(conf_path)

    t = TestConf()

    assert t.foo == 1
    assert t.bar == "hello"
    assert t.bam is None
    assert t.fang == 10
    assert t.baz == 0.9


@test
def test_nested_conf():
    @mcf.config
    class Foo:
        a: int = 1
        b: int = 2

    @mcf.config(isroot=True)
    class TestConf:
        foo: Foo
        bar: str = "hello"
        baz: float
        bam: List[int] = None
        fang = 6

    with tempfile.TemporaryDirectory() as tmpd:
        conf_path = os.path.join(tmpd, "test_conf.yaml")
        test_conf = {"foo": {"b": 3}, "baz": 0.9, "fang": 10}
        with open(conf_path, "w+") as f:
            f.write(yaml.dump(test_conf))
        mcf.load_from_file(conf_path)

    t = TestConf()

    assert t.foo.a == 1
    assert t.foo.b == 3
    assert t.bar == "hello"
    assert t.bam is None
    assert t.fang == 10
    assert t.baz == 0.9


@test
def test_double_nested_conf():
    @mcf.config
    class Foo:
        a: int = 1
        b: int = 2

    @mcf.config(isroot=True)
    class TestConf:
        foo: Foo
        bar: Foo
        baz: float
        bam: List[int] = None
        fang = 6

    with tempfile.TemporaryDirectory() as tmpd:
        conf_path = os.path.join(tmpd, "test_conf.yaml")
        test_conf = {"foo": {"b": 3}, "baz": 0.9, "fang": 10, "bar": {"a": 4}}
        with open(conf_path, "w+") as f:
            f.write(yaml.dump(test_conf))
        mcf.load_from_file(conf_path)

    t = TestConf()

    assert t.foo.a == 1
    assert t.foo.b == 3
    assert t.bar.a == 4
    assert t.bar.b == 2
    assert t.bam is None
    assert t.fang == 10
    assert t.baz == 0.9


@test
def test_deeper_nested_conf():
    @mcf.config
    class Foo:
        a: Bar
        b: int = 2

    @mcf.config
    class Bar:
        a: int = 1
        b: int = 2

    @mcf.config(isroot=True)
    class TestConf:
        foo: Foo
        bar: Bar
        baz: float
        bam: List[int] = None
        fang = 6

    with tempfile.TemporaryDirectory() as tmpd:
        conf_path = os.path.join(tmpd, "test_conf.yaml")
        test_conf = {"foo": {"a": {"a": 49}, "b": 3}, "baz": 0.9, "fang": 10, "bar": {"a": 4}}

        with open(conf_path, "w+") as f:
            f.write(yaml.dump(test_conf))
        mcf.load_from_file(conf_path)

    t = TestConf()

    assert t.foo.a.a == 49
    assert t.foo.b == 3
    assert t.bar.a == 4
    assert t.bar.b == 2
    assert t.bam is None
    assert t.fang == 10
    assert t.baz == 0.9


@test
def test_overrite_with_dict():
    @mcf.config
    class Foo:
        a: Bar
        b: int = 2

    @mcf.config
    class Bar:
        a: int = 1
        b: int = 2

    @mcf.config(isroot=True)
    class TestConf:
        foo: Foo
        bar: Bar
        baz: float
        bam: List[int] = None
        fang = 6

    with tempfile.TemporaryDirectory() as tmpd:
        conf_path = os.path.join(tmpd, "test_conf.yaml")
        test_conf = {"foo": {"a": {"a": 49}, "b": 3}, "baz": 0.9, "fang": 10, "bar": {"a": 4}}
        with open(conf_path, "w+") as f:
            f.write(yaml.dump(test_conf))
        mcf.load_from_file(conf_path)

    test_conf_2 = {"foo": {"a": {"a": 49}, "b": 52}, "baz": 0.9, "fang": 10, "bar": {"a": 4}}

    t = mcf.load_conf_from_dict(test_conf_2, TestConf)

    assert t.foo.a.a == 49
    assert t.foo.b == 52
    assert t.bar.a == 4
    assert t.bar.b == 2
    assert t.bam is None
    assert t.fang == 10
    assert t.baz == 0.9


@test
def test_save_and_load():
    @mcf.config
    class Foo:
        a: Bar
        b: int = 2

    @mcf.config
    class Bar:
        a: int = 1
        b: int = 2

    @mcf.config(isroot=True)
    class TestConf:
        foo: Foo
        bar: Bar
        baz: float
        bam: List[int] = None
        fang = 6

    t1 = TestConf()
    with tempfile.TemporaryDirectory() as tmpd:
        conf_path = os.path.join(tmpd, "test_conf.yaml")
        mcf.save_to_file(t1, conf_path)
        mcf.load_from_file(conf_path)
    t2 = TestConf()

    assert t1.foo.a.a == t2.foo.a.a
    assert t1.foo.b == t2.foo.b
    assert t1.bar.a == t2.bar.a
    assert t1.bar.b == t2.bar.b
    assert t1.bam == t2.bam
    assert t1.fang == t2.fang
    assert t1.baz == t2.baz


@test
def test_list_elements():
    @mcf.config
    class Foo:
        a: int = 1
        b: int = 2

    @mcf.config(isroot=True)
    class TestConf:
        baz: float
        bam: List[Foo] = None
        fang = 6

    with tempfile.TemporaryDirectory() as tmpd:
        conf_path = os.path.join(tmpd, "test_conf.yaml")
        test_conf = {
            "baz": 2.0,
            "bam": [
                {"a": 5},
                {"b": 6},
            ],
        }
        with open(conf_path, "w+") as f:
            f.write(yaml.dump(test_conf))
        mcf.load_from_file(conf_path)
    t = TestConf()

    assert t.bam[0].a == 5
    assert t.bam[0].b == 2
    assert t.bam[1].a == 1
    assert t.bam[1].b == 6
    assert t.baz == 2.0
    assert t.fang == 6

    with tempfile.TemporaryDirectory() as tmpd:
        conf_path = os.path.join(tmpd, "test_conf.yaml")
        mcf.save_to_file(t, conf_path)
        mcf.load_from_file(conf_path)
        t2 = TestConf()

    assert t2.bam[0].a == 5
    assert t2.bam[0].b == 2
    assert t2.bam[1].a == 1
    assert t2.bam[1].b == 6
    assert t2.baz == 2.0
    assert t2.fang == 6


def run_tests():
    failed = []
    for f in _TEST_F:
        print(f"[TEST]: Running test: {f.__name__}")
        try:
            f()
        except Exception as e:
            failed.append(f)
            print(traceback.format_exc())
            print(f"\033[31m[TEST]: Failed with the following error: {e}\033[0m")
        else:
            print("\033[32m[TEST]: Test ran successfully\033[0m")
        finally:
            print("[TEST]: -------------------------------------------")

    if failed:
        print("\033[31m[TEST]: Failed Tests\033[0m")
        print("\033[31m[TEST]: Failed tests: \033[0m")
        for fail in failed:
            print(f"\033[31m[Test]:     {fail.__name__}\033[0m")
        sys.exit(1)
    else:
        print("\033[32m[TEST]: Tests successful\033[0m")
        sys.exit(0)


if __name__ == "__main__":
    run_tests()
