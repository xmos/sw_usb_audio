""" This file lists all the configs used in each test. """
from collections import namedtuple
from dataclasses import dataclass, field
import itertools
from typing import List
import pytest


@dataclass
class ConfigDescriptor:
    """ All List types in the descriptor will be added as test combinations
    And must end with an 's'! e.g. .rates in the descriptor becomes .rate in the test
    """

    app: str
    config: str
    chans_in: int
    chans_out: int
    analogue_input: bool = True
    analogue_output: bool = True
    dfu: bool = False
    dsd: bool = False
    spdif: bool = False
    rates: List[int] = field(default_factory=list)


def unpack_descriptor(desc: ConfigDescriptor):
    """ Returns all test combinations described by the descriptor """

    iterator_attrs = [k for k in desc.__dict__ if type(getattr(desc, k)) is list]
    fixed_attrs = [k for k in desc.__dict__ if k not in iterator_attrs]

    settings = []
    iter_keys = []
    for attr in iterator_attrs:
        settings.append(getattr(desc, attr))
        iter_keys.append(attr)
    # Creates a "set-combination" of all the List settings
    # e.g. [1, 2], [3, 4] becomes [1, 3], [1, 4], [2, 3], [2, 4]
    combos = list(itertools.product(*settings))

    ConfigInstance = namedtuple(
        "ConfigInstance",
        # Take the 's' off the end of each iterator attr
        # i.e. 'rates' becomes 'rate'
        [k[:-1] for k in iterator_attrs] + fixed_attrs,
    )

    configs = []
    for combo in combos:
        instance_dict = {}
        for i, key in enumerate(iter_keys):
            # Take the 's' off the end of each iterator attr
            # i.e. 'rates' becomes 'rate'
            instance_dict[key[:-1]] = combo[i]
        for key in fixed_attrs:
            instance_dict[key] = getattr(desc, key)
        configs.append(ConfigInstance(**instance_dict))
    return configs


# The config descriptors
descriptors = [
    ConfigDescriptor("xk_216_mc", "2i10o10xxxxxx", 8, 8, rates=[48000]),
    ConfigDescriptor("xk_216_mc", "2i2o2xxxxxd", 2, 2, rates=[48000], dsd=True),
]

configs = list(itertools.chain(*[unpack_descriptor(d) for d in descriptors]))

# Test
print(configs)
