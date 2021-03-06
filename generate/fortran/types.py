# -* coding: utf-8 -*
"""
This module generate chemfiles main (fortran) types and bind specific functions
to them, using the name of the function.
"""
from collections import OrderedDict
from .constants import BEGINING, FORTRAN_TYPES
from .convert import function_name_to_fortran
from generate.functions import FREE_FUNCTIONS

TEMPLATE = """
type {name}
    private
    type(c_ptr) :: ptr
contains
{procedures}
end type
"""


class BoundProcedure:
    '''Class reprensenting a bound procedure for a Fortran type'''

    def __init__(self, name, procedure):
        self.name = name
        self.procedure = procedure

    def __str__(self):
        return "procedure :: {name} => {proc}".format(name=self.name,
                                                      proc=self.procedure)


class Type:
    '''Class reprensenting a Fortran type'''

    def __init__(self, name):
        self.name = name
        self.procedures = []

    def add_procedure(self, proc):
        self.procedures.append(proc)

    def __str__(self):
        tmp = ""
        for proc in self.procedures:
            tmp += "    {proc}\n".format(proc=str(proc))
        tmp = tmp[:-1]  # Remove last \n
        return TEMPLATE.format(name=self.name, procedures=tmp)


def write_types(path, functions):
    '''
    Generate types definitions for the fortran interface.
    '''
    types = OrderedDict()
    for name in FORTRAN_TYPES:
        types[name] = Type(name)

    for function in functions:
        if function.name in FREE_FUNCTIONS:
            continue
        elif function.name.endswith("get_property"):
            type = types["chfl_property"]
            member_name = "from_" + function.name.split("_")[1]
            type.add_procedure(
                BoundProcedure(member_name, function_name_to_fortran(function))
            )
        else:
            typename = function.typename
            if typename is None:
                continue
            else:
                typename = typename.lower()

            type = types[typename]

            member_name = function.member_name
            if not member_name:
                member_name = "init"

            type.add_procedure(
                BoundProcedure(member_name, function_name_to_fortran(function))
            )

    with open(path, "w") as fd:
        fd.write(BEGINING)
        for type_ in types.values():
            fd.write(str(type_))
