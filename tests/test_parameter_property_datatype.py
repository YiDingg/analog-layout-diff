"""A parameter property may hold a datatype the master's definition does not.

OA validates a property name against the pcelle parameter definitions when
``dbReplaceProp`` writes it and refuses a datatype that differs from the
definition ("DB-270000: Datatype for input parameter 'm' does not match the
definition"). A source layout may still hold that state -- a schematic
multiplier ``m = "1"`` copied onto an integer parameter is a common one -- and
only the creation call writes it, because it takes (name type value) triples
without consulting the definition. The replay therefore hands the recorded
property type/value to the creation call and must not attempt to replace that
property afterwards.

Measured on both OA generations this tool runs on -- OA 22.60 (IC618) and
OA 22.61 (IC23.1): the creation call writes the property from its
(name type value) triples on either, and ``dbReplaceProp`` returns nil for that
name on either, including when the existing property already carries the
requested datatype. The state is not version-dependent.
"""
from layoutdiff.data.core import canonicalize
from layoutdiff.eda.virtuoso.adapter import creation_parameters, render
from layoutdiff.eda.virtuoso.support import coverage


def records():
    return [
        dict(kind='cell', name='', dbu=1000, units='micron', cellType='maskLayout',
             technology='test', props=[], sitePattern=None),
        dict(kind='net', name='iref', props=[], sigType='signal', isGlobal=None,
             connStatus=None, criticality=None, routePattern=None, source=None),
        dict(kind='inst', name='MREF', libName='EXAMPLE_TECH', cellName='example_nmos',
             viewName='layout', pcell=True, numInst=1, physOnly=None, status=None,
             source='netlist', xy=[0, 0], orient='R0', group=None,
             props=[['m', 'string', '1'], ['fingers', 'int', 2], ['note', 'string', 'keep']],
             params=[['fingers', 'int', 2], ['m', 'int', 1], ['w', 'float', 1.0]],
             connections=[['D', 'iref', []]]),
    ]


def test_parameter_property_datatype_is_written_by_the_creation_call_only():
    snapshot = canonicalize(records())
    assert not coverage(snapshot)
    text = '\n'.join(render(snapshot))
    assert 'list("m" "string" "1")' in text
    assert 'list("m" "int" 1)' not in text
    assert 'dbReplaceProp(o "m"' not in text
    # A parameter whose property agrees with the definition replays as before,
    # and so does an ordinary instance property.
    assert 'dbReplaceProp(o "fingers" "int" 2)' in text
    assert 'dbReplaceProp(o "note" "string" "keep")' in text


def test_agreeing_parameter_types_keep_the_recorded_parameter_list():
    record = records()[2]
    parameters, applied = creation_parameters(record)
    assert applied == {'m'}
    assert ['m', 'string', '1'] in parameters
    assert ['w', 'float', 1.0] in parameters

    record['props'] = [['m', 'int', 1]]
    parameters, applied = creation_parameters(record)
    assert applied == set()
    assert ['m', 'int', 1] in parameters
