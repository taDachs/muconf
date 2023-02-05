# ⚙️ muconf

Python modules for creating injectable typed configurations that can be easily
serialized to and from yaml files.

## Example
```python
import muconf as mcf

# create a configuration class
@mcf.config
class FooConf:
    a: int = 2
    b: int = 3

# supports nesting
@mcf.config
class BarConf:
    foo: Foo
    bar: float

# load config from file
mcf.load_from_file(config_path)
conf = BarConf()

# or initialize a config object from a dict
conf = mcf.load_conf_from_dict(test_conf_2, BarConf)

# save config to file
mcf.save_to_file(conf, test_conf_2)
```
