from lcall.owlRdyDatatypeProperty import OwlRdyDatatypeProperty
from lcall.owlRdyObjectProperty import OwlRdyObjectProperty
from lcall.owlRdyClass import OwlRdyClass


class ResultList:

    def __init__(self, assertions: list[(tuple[OwlRdyDatatypeProperty, int] |
                                         tuple[OwlRdyObjectProperty, OwlRdyClass, list])]):
        self.assertions = assertions

    def __repr__(self):
        return str(self.assertions)

    def __iter__(self):
        return iter(self.assertions)
