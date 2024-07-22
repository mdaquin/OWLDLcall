from lcall.DLClass import DLClass
from lcall.DLDatatype import DLDatatype
from lcall.DLDatatypeProperty import DLDatatypeProperty
from lcall.DLProperty import DLProperty
from lcall.callableThing import CallableThing
from lcall.DLPropertyChain import DLPropertyChain
from lcall.resultList import ResultList
import logging
from typing import Any, Iterable


def is_a_container(var: Any) -> bool:
    """
    Check if the variable is a container, i.e. contains multiples elements

    :return True if the variable is a list, tuple, set or dictionary
    """
    return isinstance(var, Iterable) and not isinstance(var, str)


def convert_to(value: Any, _type: (type | None)) -> Any:
    """
    Convert the value to a certain type (or just return the value if the type is None)
    If the value is a list or tuple, it is converted to a string as containers can't be datatype properties.
    
    :param value: the value to convert
    :param _type: the type of the new value
    :return the converted (if possible) value
    """
    if _type is bool:  # not sure about that
        return value not in ("false", "False", "0", False, 0)
    if is_a_container(value):
        logging.warning("Datatype properties can't have multiple values, the container is casted as a string.")
        return str(value)
    # if the range of the property was not specified
    if _type is None:
        return value
    return _type(value)


class CallFormula:
    """
    Object representing a call formula
    """

    def __init__(self, name: str, subsuming_property: DLProperty, function: CallableThing,
                 parameters: list[DLPropertyChain], call_domain: DLClass, call_range: (DLDatatype | DLClass),
                 result_list: (ResultList | None)):
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
        self.result_list = result_list

    def get_subsuming_property(self) -> DLProperty:
        return self._subsuming_property

    def get_parameters(self) -> list[DLPropertyChain]:
        return self._parameters

    def get_domain(self) -> DLClass:
        return self._domain

    def get_range(self) -> (DLDatatype | DLClass):
        return self._range

    def get_result_list(self) -> (ResultList | None):
        return self.result_list

    def is_a_datatype_call(self) -> bool:
        """
        Check if the call subsuming property is a datatype property

        :return: True if the call subsuming property is a datatype property, False otherwise.
        """
        return isinstance(self._subsuming_property, DLDatatypeProperty)

    def exec(self, params: list[DLPropertyChain]) -> (list | None):
        """
        Executes the call formula function, and, basically returns the result.

        :param params: parameter values to use
        :return: the result of the execution of the function
        """
        value = self._function.exec(params)
        if value is None:
            return None
        if self.is_a_datatype_call():
            # support for multi values
            # for example, if we want to add both p(a, 0) and p(a, 1), 
            # we can make the function return [0, 1]
            if not is_a_container(value):
                value = [value]
            for i in range(len(value)):
                value[i] = convert_to(value[i], self.get_range().get())
        else:
            # if it's a object property call formula, the the result of the function should be a tuple/list
            # but we support the result not being a tuple, if it is only one value
            if not isinstance(value, (list, tuple)):
                value = (value,)
        return value

    def __repr__(self):
        return self.name
