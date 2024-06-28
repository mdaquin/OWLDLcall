from lcall.DLClass import DLClass
from lcall.DLDatatype import DLDatatype
from lcall.DLDatatypeProperty import DLDatatypeProperty
from lcall.DLProperty import DLProperty
from lcall.DLPropertyChain import DLPropertyChain
from lcall.callableThing import CallableThing
from lcall.DLPropertyChain import DLPropertyChain
import logging
from typing import Any


def is_a_container(var: Any) -> bool:
    """
    Check if the variable is a container, i.e. contains multiples elements

    :return True if the variable is a list, tuple, set or dictionary
    """
    return isinstance(var, (list, tuple, set, dict))


def convert_to(value: Any, type: (type | None)) -> Any:
    """
    Convert the value to a certain type (or just return the value if the type is None)
    
    :param value: the value to convert
    :param type: the type of the new value
    :return the converted value (or the just value if the type is None)
    """
    # if the range of the property was not specified
    if type is None:
        return value
    if type is bool: # not sure about that
        return type(value not in ("false", "False", "0", False, 0))
    return type(value)


class CallFormula:
    """
    Object representing a call formula
    """

    def __init__(self, name: str, subsuming_property: DLProperty, function: CallableThing, 
                 parameters: list[DLPropertyChain], call_domain: DLClass, call_range: (DLDatatype | DLClass)):
        """
        Create a call formula object from its function, parameters, domain and datatype range

        :param name: the name of the call (instance)
        :param subsuming_property: the datatype property subsuming the call formula
        :param function: function to be called
        :param parameters: the parameters of the call formula
        :param call_domain: domain of the call formula
        :param call_range: range of the call formula
        """
        self.name = name
        self._subsuming_property = subsuming_property
        self._function = function
        self._parameters = parameters
        self._domain = call_domain
        self._range = call_range

    def get_subsuming_property(self) -> DLProperty:
        return self._subsuming_property

    def get_parameters(self) -> list[DLPropertyChain]:
        return self._parameters

    def get_domain(self) -> DLClass:
        return self._domain

    def get_range(self) -> (DLDatatype | DLClass):
        return self._range
    
    def is_a_datatype_call(self) -> bool:
        """
        Check if the call subsuming property is a datatype property

        :return: True if the call subsuming property is a datatype property, False otherwise.
        """
        return isinstance(self._subsuming_property, DLDatatypeProperty)

    def exec(self, params: list[DLPropertyChain]) -> Any:
        """
        Executes the call formula function, and returns the result
        (Does a bit of conversion in case it's a datatype call i.e. a call for a datatype property)

        :param params: parameter values to use
        :return: the result of the execution of the function
        """
        value = self._function.exec(params)
        # if the result is None, there's nothing to do
        # if it's a call for an object property, this class doesn't handle that
        if value is None or not self.is_a_datatype_call():
            return value
        # here, we know it's a call for a datatype property
        value = convert_to(value, self.get_range().get())
        # datatype properties can't be containers, and if the declared type doesn't change it, we force it to string
        if is_a_container(value):
            logging.warning("Multiple values returned, without a proper range.\nDatatype properties can't have multiple values, the container is casted as a string.")
            value = str(value)
        
        return value

    def __repr__(self):
        return self.name