from __future__ import annotations

import re
from pydoc import locate
from typing import Any

import yaml

__version__ = "0.0.1"

_C = {}
_CLS = {}
_MUCONF = "__muconf"
_LIST_PATTERN = re.compile(r"^[Ll]ist\[(\w*)\]$")


def load_from_file(path: str):
    global _C
    with open(path, "r") as f:
        _C = yaml.load(f, Loader=yaml.FullLoader)


def load_conf_from_dict(dict_: dict, cls: type) -> Any:
    return cls(root=dict_)


def save_to_file(conf: Any, path: str):
    with open(path, "w+") as f:
        f.write(yaml.dump(conf.asdict()))


def _is_conf_type(type_: type) -> bool:
    return hasattr(type_, _MUCONF)


def _get_type_from_str(s: str) -> type:
    if s in _CLS:
        return _CLS[s]

    if re.match(_LIST_PATTERN, s):
        m = re.search(_LIST_PATTERN, s)
        t = m.group(1)
        if t in _CLS:
            return list

    return locate(s)

    raise ValueError(f"{s} has not yet been registered as config")


def _is_conf_subtype(s: str) -> bool:
    if s in _CLS:
        return True

    if re.match(_LIST_PATTERN, s):
        m = re.search(_LIST_PATTERN, s)
        t = m.group(1)
        if t in _CLS:
            return True

    return False


def _get_list_type(s: str) -> bool:
    m = re.search(_LIST_PATTERN, s)
    t = m.group(1)
    if t in _CLS:
        return _CLS[t]


def _handle_nested_configs(root: dict, field: str, annotation: str) -> Any:
    type_ = _get_type_from_str(annotation)
    if type_ == list:
        # list as subfield
        type_ = _get_list_type(annotation)
        field_elems = [type_(elem) for elem in root.get(field, [])]
        for elem in root.get(field, []):
            field_elems.append(type_(elem))
        return field_elems
    else:
        # subfield is not list
        return type_(root.get(field, {}))


def config(cls: type = None, isroot: bool = False) -> callable[[type], type] | type:
    def f(cls: type) -> type:
        attrs = [
            attr for attr in dir(cls) if not (callable(getattr(cls, attr)) or attr.startswith("__"))
        ]
        annotations = cls.__annotations__
        fields = set(annotations.keys()) | set(attrs)

        _CLS[cls.__name__] = cls

        def __init__(self, root: dict = None):
            if root is None:
                if isroot:
                    root = _C
                elif cls.__name__ in _C:
                    root = _C[cls.__name__]
                else:
                    root = {}

            for field in fields:
                if field in annotations and _is_conf_subtype(annotations[field]):
                    # field has annotation and is either config or list of config
                    setattr(self, field, _handle_nested_configs(root, field, annotations[field]))
                elif field in root:
                    # has set value in config
                    setattr(self, field, root[field])
                elif field in attrs:
                    # has default
                    setattr(self, field, getattr(cls, field))
                else:
                    # missing value
                    raise ValueError(f"{field} doesn't have a set value nor a default value")

        def asdict(self) -> dict:
            dict_ = {}
            for field in fields:
                if field in annotations and _is_conf_subtype(annotations[field]):
                    # nested config
                    type_ = _get_type_from_str(annotations[field])
                    if type_ == list:
                        dict_[field] = [elem.asdict() for elem in getattr(self, field)]
                    else:
                        dict_[field] = getattr(self, field).asdict()
                else:
                    dict_[field] = getattr(self, field)

            return dict_

        def __str__(self) -> str:
            dict_ = self.asdict()
            return yaml.dump(dict_)

        setattr(cls, "__init__", __init__)
        setattr(cls, "asdict", asdict)
        setattr(cls, "__str__", __str__)
        setattr(cls, _MUCONF, True)

        return cls

    if cls is None:
        return f
    else:
        return f(cls)
