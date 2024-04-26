from lcall.DLClass import DLClass
from lcall.DLDatatype import DLDatatype
from lcall.DLProperty import DLProperty
from lcall.DLInstance import DLInstance
from lcall.DLPropertyChain import DLPropertyChain
from lcall.functionCall import FunctionCall
from lcall.classAssertion import ClassAssertion
from lcall.datatypePropertyAssertion import DatatypePropertyAssertion
from lcall.objectPropertyAssertion import ObjectPropertyAssertion

# if there are conversion problems
def convert(toType, valueToConvert):
    if toType is None:
        return valueToConvert
    if toType is bool:
        return toType(valueToConvert not in ("false", "False", "0", False, 0))
    else:
        return toType(valueToConvert)

def areEqual(inst, values):
    same = True
    for prop, value in values.items():
        prop_range_type = prop.get().range[0]

        # if the property is an object property
        if isinstance(value, dict):
            # we get every value of the property for the instance
            attr = getattr(inst, prop.get().name, [])
            # if there is no value, it doesn't match cause we will create one
            if not attr:
                return False
            # if there are, we check if one of them matches
            else:
                return same and any([areEqual(x, value) for x in attr])
        else:
            v = convert(prop_range_type, value)
            same = same and v in getattr(inst, prop.get().name, [])
    return same
    
class CallFormula:
    """
    Object representing a call formula
    """

    def __init__(self, name: str, subsuming_property: DLProperty, functionCall: FunctionCall, call_domain: DLClass, call_range: (DLDatatype | DLClass)):
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

    def get_range(self) -> (DLDatatype | DLClass):
        return self._range
    
    def get_instances(self):
        return self._domain.get().instances()

    def exec(self, instance: DLInstance, params: list, assertions, instances = None) -> None:
        """
        Execute the call formula calculation and update assertions

        :param instance: instance from which the parameters are derived
        :param params: parameter values to use
        :param assertions: the list current assertions to update
        :return true if new assertions were inferred
        """
        
        # if the subsuming property is functional and the instance already has the property defined, there is no need to call anything
        attr = getattr(instance.get(), self._subsuming_property.get().name, None)
        if attr is not None and not isinstance(attr, list):
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

            # for non functional properties, we check if the value doesn't already exist
            if attr is not None and call_result in attr:
                return None
            
            assertions.append(DatatypePropertyAssertion(self._subsuming_property, instance, call_result))
        else:
            # here, the range is a concept

            # for non functional properties, we need to check if the instance doesn't already exist
            # (well it doesn't, but we'll check every associated datatype properties)
            if attr is not None and any([areEqual(c, call_result) for c in attr]):
                return None
            
            # creates the instance of the concept with a unique name
            c = ClassAssertion(range_type)
            if instances is not None:
                instances.append(c.instance)
            assertions.append(ObjectPropertyAssertion(self._subsuming_property, instance, c.get_instance()))
            assertions.append(c)
            # "fill" the necessary properties of the new instance and add the associated assertions
            self.fillProperties(c.get_instance(), call_result, assertions, instances)
    
    def fillProperties(self, instance, call_result, assertions, instances = None):
        for prop, value in call_result.items():
            # we get the range is specified
            # if not, and it is an object property, we'll create a Thing instance
            # if it is a datatype property, we'll take the result of the function without trying to convert
            prop_range_type = prop.get().range[0] if prop.get().range else None
            # if there is an object property
            # create the necessary instance and fill its properties recursively
            # then fill the object property
            if isinstance(value, dict):
                # create the new instance for the object property
                c = ClassAssertion(prop_range_type)
                # save the new instance for future calls
                if instances is not None:
                    instances.append(c.instance)
                assertions.append(ObjectPropertyAssertion(prop, instance, c.get_instance()))
                assertions.append(c)
                self.fillProperties(c.get_instance(), value, assertions, instances)
            else:
                d = None
                if isinstance(value, list) and (type(value) is not str):
                    d = DatatypePropertyAssertion(prop, instance, [convert(prop_range_type, x) for x in value], True)
                else:
                    d = DatatypePropertyAssertion(prop, instance, convert(prop_range_type, value))
                assertions.append(d)

    def __repr__(self):
        return self.name