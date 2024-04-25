from typing import Union # allows us to define 2 classes as the type of an argument
from lcall.DLClass import DLClass
from lcall.DLDatatype import DLDatatype
from lcall.DLProperty import DLProperty
from lcall.DLInstance import DLInstance
from lcall.DLPropertyChain import DLPropertyChain
from lcall.functionCall import FunctionCall
from lcall.propertyAssertion import PropertyAssertion
from lcall.datatypePropertyAssertion import DatatypePropertyAssertion
from lcall.objectPropertyAssertion import ObjectPropertyAssertion

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

    def __init__(self, name: str, subsuming_property: DLProperty, functionCall: FunctionCall, call_domain: DLClass, call_range: Union[DLDatatype, DLClass]):
        """
        Create a call formula object from its function (arbitrary), parameters, domain and datatype range

        :param subsuming_property: the datatype property subsuming the call formula
        :param functionCall: function to be called
        :param call_domain: domain of the call formula
        :param call_range: range of the call formula
        """
        self.name = name
        self._subsuming_property = subsuming_property
        self._functionCall = functionCall
        self._domain = call_domain
        self._range = call_range

    def get_subsuming_property(self) -> DLProperty:
        return self._subsuming_property

    def get_parameters(self) -> list[DLPropertyChain]:
        return self._functionCall.get_parameters()

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
        call_result = self._functionCall.exec(params)
        # Get first datatype in property range (as we can't know which one it will be)
        range_type = self._range.get()

        if call_result == None:
            return None
        elif isinstance(self.get_range(), DLDatatype):
            if range_type is not None:
                # Cast value result as wanted type
                call_result = convert(range_type, call_result)
            return DatatypePropertyAssertion(self._subsuming_property, instance, call_result)
        else:
            value = None
            # here, the range is a concept
            if range_type is not None:
                # creates the instance of the concept with a unique name
                value = range_type()
                # fill in the datatypeProperties
                self.fillProperties(value, call_result)
            else:
                return None
            return ObjectPropertyAssertion(self._subsuming_property, instance, value)
    
    def fillProperties(self, instance, call_result):
        for prop, value in call_result.items():
            prop_range_type = prop.range[0]
            # if there is an object property
            # create the necessary instance and fill its properties recursively
            # then fill the object property
            if isinstance(value, dict):
                new_instance = prop_range_type()
                self.fillProperties(new_instance, value)
                prop[instance].append(new_instance)
            else:
                if isinstance(value, list) and (type(value) is not str):
                    prop[instance] = [convert(prop_range_type, x) for x in value]
                elif type(value) is str:
                    # putting the string into a list prevents it from creating multiple properties for each character
                    prop[instance] = [convert(prop_range_type, value)]
                else:
                    prop[instance] = convert(prop_range_type, value)


    def __repr__(self):
        # return str(self._subsuming_property) + " subsuming call(" + str(self._functionCall) + ", " + str(self._domain) + ", " + str(self._range) + ")"
        return self.name
    
