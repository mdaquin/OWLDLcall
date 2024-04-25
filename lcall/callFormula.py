from typing import Union # allows us to define 2 classes as the type of an argument
from lcall.DLClass import DLClass
from lcall.DLDatatype import DLDatatype
from lcall.DLProperty import DLProperty
from lcall.DLInstance import DLInstance
from lcall.DLPropertyChain import DLPropertyChain
from lcall.functionCall import FunctionCall
from lcall.classAssertion import ClassAssertion
from lcall.owlRdyInstance import OwlRdyInstance
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
    
    def get_instances(self):
        return self._domain.get().instances()

    def exec(self, instance: DLInstance, params: list, assertions, new_instances) -> None:
        """
        Execute the call formula calculation and update assertions

        :param instance: instance from which the parameters are derived
        :param params: parameter values to use
        :param assertions: the list current assertions to update
        :return true if new assertions were inferred
        """
        
        # if the subsuming property is functional and the instance already has the property defined, there is no need to call anything
        # it replaces the is_asserted method
        attr = getattr(instance.get(), self._subsuming_property.get().name, None)
        if attr != None and not isinstance(attr, list):
            return

        call_result = self._functionCall.exec(params)
        # Get the class of the range (to create a new instance or convert to the correct type)
        range_type = self._range.get()

        if call_result == None:
            return
        elif isinstance(self.get_range(), DLDatatype):
            # here the range is a datatype

            # Cast value result as wanted type
            call_result = convert(range_type, call_result)
            assertions.append(DatatypePropertyAssertion(self._subsuming_property, instance, call_result))
        else:
            # here, the range is a concept

            # creates the instance of the concept with a unique name
            c = ClassAssertion(range_type)
            new_instances.append(c.instance)
            assertions.append(ObjectPropertyAssertion(self._subsuming_property, instance, c.get_instance()))
            assertions.append(c)
            # "fill" the necessary properties of the new instance and add the associated assertions
            self.fillProperties(c.get_instance(), call_result, assertions, new_instances)
    
    def fillProperties(self, instance, call_result, assertions, new_instances):
        for prop, value in call_result.items():
            prop_range_type = prop.get().range[0]
            # if there is an object property
            # create the necessary instance and fill its properties recursively
            # then fill the object property
            if isinstance(value, dict):
                # create the new instance for the object property
                c = ClassAssertion(prop_range_type)
                # save the new instance for future calls
                new_instances.append(c.instance)
                assertions.append(ObjectPropertyAssertion(prop, instance, c.get_instance()))
                assertions.append(c)
                self.fillProperties(c.get_instance(), value, assertions, new_instances)
            else:
                d = None
                if isinstance(value, list) and (type(value) is not str):
                    d = DatatypePropertyAssertion(prop, instance, [convert(prop_range_type, x) for x in value], True)
                else:
                    d = DatatypePropertyAssertion(prop, instance, convert(prop_range_type, value))
                assertions.append(d)

    def __repr__(self):
        return self.name