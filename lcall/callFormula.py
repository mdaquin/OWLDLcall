from lcall.DLClass import DLClass
from lcall.DLDatatype import DLDatatype
from lcall.DLDatatypeProperty import DLDatatypeProperty
from lcall.DLInstance import DLInstance
from lcall.DLPropertyChain import DLPropertyChain
from lcall.callableThing import CallableThing
from lcall.datatypePropertyAssertion import DatatypePropertyAssertion

class CallFormula:
    """
    Object representing a call formula
    """

    def __init__(self, subsuming_property: DLDatatypeProperty, function_to_call: CallableThing, params: list[DLPropertyChain], call_domain: DLClass, call_range: DLDatatype):
        """
        Create a call formula object from its function (arbitrary), parameters, domain and datatype range

        :param subsuming_property: the datatype property subsuming the call formula
        :param function_to_call: function to be called
        :param params: parameters of the call formula
        :param call_domain: domain of the call formula
        :param call_range: range of the call formula
        """
        self._subsuming_property = subsuming_property
        self._function_to_call = function_to_call
        self._params = params
        self._domain = call_domain
        self._range = call_range

    def get_subsuming_property(self) -> DLDatatypeProperty:
        return self._subsuming_property

    def get_parameters(self) -> list[DLPropertyChain]:
        return self._params

    def get_domain(self) -> DLClass:
        return self._domain

    def get_range(self) -> DLDatatype:
        return self._range

    def exec(self, instance: DLInstance, params: list) -> DatatypePropertyAssertion:
        """
        Execute the call formula calculation and return assertions

        :param instance: instance from which the parameters are derived
        :param params: parameter values to use
        :return: result of the execution of the function
        """
        call_result = self._function_to_call.exec(params)
        return DatatypePropertyAssertion(self._subsuming_property, instance, call_result) if call_result is not None else None

    def __repr__(self):
        return str(self._subsuming_property) + " subsuming call(" + str(self._function_to_call) + ", " + str(self._params) + ", " + str(self._domain) + ", " + str(self._range) + ")"
