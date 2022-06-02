### main deps
from amaranth import *
from amaranth.build import Platform
from typing import List, Dict, Tuple, Optional
### test deps ###
from amaranth.asserts import * # AnyConst, AnySeq, Assert, Assume, Cover, Past, Stable, Rose, Fell, Initial

def createVerificationSpec(ports_map:Dict, inputs_sequence:List[Dict], expected_output:Dict):
    """
    Create a structure containing the definition of a formal verification :

    ```
    # inside code to generate formal verification
    assertSpec = createVerificationSpec(...)
    with m.If(assertSpec.conditions):
        m.d.sync += Assert(assertSpec.expected)
    ```

    Parameters
    ----------
    ports_map : a dictionnary, associating a name (e.g. 'rst') to a Signal.
    inputs_sequence : a list of steps in chronological order. Each step is a dictionnary of names (as in the ports_map)
      associated to a value. If there is 2 steps, the first step evaluates each (key,value) as `(Past(ports_map[key],2) = value)`, joined by
      '&'. Then the whole sequence is joined by '&'
    expected_output : a dictionnary of names (as in the ports_map) associated as a value. Each item is evaluated as `(ports_map[key] = value)`
      and joined by '&'
    """
    result = {}
    conditions = []
    step_count = 1
    for step in reversed(inputs_sequence)
        past_items = [(Past(ports_map[key],step_count) = value) for key, value in step]

        for index in range(len(past_items)):
            condition_set = (past_items[index]) if index = 0 else (condition_set & past_items[index])

        conditions.append(condition_set)
        step_count += 1

    for index in range(len(conditions)):
        result.conditions = conditions[index] if index = 0 else (result.conditions & conditions[index])

    expected = [(ports_map[key] = value) for key, value in expected_output]

    for index in range(len(expected)):
        result.expected = expected[index] if index = 0 else (result.expected & expected[index])

    return result
