from typing import Union # allows us to define 2 classes as the type of an argument
from lcall.DLClass import DLClass
from lcall.DLDatatype import DLDatatype
from lcall.DLProperty import DLProperty
from lcall.DLInstance import DLInstance
from lcall.DLPropertyChain import DLPropertyChain
from lcall.callableThing import CallableThing
from lcall.propertyAssertion import PropertyAssertion
from lcall.datatypePropertyAssertion import DatatypePropertyAssertion
from lcall.objectPropertyAssertion import ObjectPropertyAssertion
from owlready2 import owl

# if there are conversion problems
def convert(toType, valueToConvert):
    if toType is bool:
        return toType(valueToConvert not in ("false", "False", "0", False, 0))
    else:
        return toType(valueToConvert)
    
class CallFormula:
    """
    Object representing a call formula
    """

    def __init__(self, subsuming_property: DLProperty, function_to_call: CallableThing, params: list[DLPropertyChain], call_domain: DLClass, call_range: Union[DLDatatype, DLClass]):
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

    def get_subsuming_property(self) -> DLProperty:
        return self._subsuming_property

    def get_parameters(self) -> list[DLPropertyChain]:
        return self._params

    def get_domain(self) -> DLClass:
        return self._domain

    def get_range(self) -> Union[DLDatatype, DLClass]:
        return self._range

    def exec(self, instance: DLInstance, params: list) -> PropertyAssertion:
        """
        Execute the call formula calculation and return assertions

        :param instance: instance from which the parameters are derived
        :param params: parameter values to use
        :return: result of the execution of the function
        """
        call_result = self._function_to_call.exec(params)
        # Get first datatype in property range (as we can't know which one it will be)
        range_type = self._range.get()

        if call_result == None:
            return None
        elif isinstance(self.get_range(), DLDatatype):
            # the range is a datatype

            if range_type is not None:
                # Cast value result as wanted type (useless for a python function)
                call_result = convert(range_type, call_result)
            return DatatypePropertyAssertion(self._subsuming_property, instance, call_result)
        else:
            # here, the range is a concept
            value = None
            if range_type is not None:
                # creates the instance of the concept with a unique name
                value = range_type()
                # if multiple data properties have to be filled,
                # the function should return a list of objects, one for each data property declared in the annotation 'hasDataProperty'
                props = []
                for x in range_type.ancestors():
                    try:
                        props.extend(x.hasDatatypeProperty)
                    except AttributeError:
                        # means there is no dataTypeProperty
                        pass
                if len(props) != len(call_result):
                    return None
                for i in range(len(props)):
                    prop_range_type = props[i].range[0]
                    props[i][value] = [convert(prop_range_type, x) for x in call_result[i]]
            return ObjectPropertyAssertion(self._subsuming_property, instance, value)

    def __repr__(self):
        return str(self._subsuming_property) + " subsuming call(" + str(self._function_to_call) + ", " + str(self._params) + ", " + str(self._domain) + ", " + str(self._range) + ")"
