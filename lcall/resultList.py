from lcall.DLDatatype import DLDatatype
from lcall.DLDatatypeProperty import DLDatatypeProperty
from lcall.DLClass import DLClass
from lcall.DLObjectProperty import DLObjectProperty


class ResultList:

    def __init__(self, assertions: list[tuple[(DLObjectProperty | DLDatatypeProperty), 
                                              (DLClass | DLDatatype), (int | list)]]):
        self.assertions = assertions

    def __repr__(self):
        return str(self.assertions)

    def __iter__(self):
        return iter(self.assertions)
