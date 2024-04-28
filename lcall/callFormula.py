from lcall.DLClass import DLClass
from lcall.DLDatatype import DLDatatype
from lcall.DLDatatypeProperty import DLDatatypeProperty
from lcall.DLProperty import DLProperty
from lcall.DLInstance import DLInstance
from lcall.DLPropertyChain import DLPropertyChain
from lcall.functionCall import FunctionCall
from lcall.classAssertion import ClassAssertion
from lcall.datatypePropertyAssertion import DatatypePropertyAssertion
from lcall.objectPropertyAssertion import ObjectPropertyAssertion


def convert(toType, valueToConvert):
    # if the range of the property was not specified
    if toType is None:
        return valueToConvert
    if toType is bool:
        return toType(valueToConvert not in ("false", "False", "0", False, 0))
    else:
        return toType(valueToConvert)

def areEqual(inst, values):
    same = True
    for property, isDatatype, value in values:
        prop = property.get()
        prop_range_type = prop.range[0] if prop.range else None

        # if the property is an object property
        if not isDatatype:
            # we get every value of the property for the instance
            # if there is no value, it doesn't match cause we will create one
            # if there are, we check if one of them matches
            same = same and any([areEqual(x, value) for x in prop[inst]])
        else:
            same = same and convert(prop_range_type, value) in prop[inst]
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
        # if the subsuming property is functional owldlready2 will return None or the value instead of a list of values
        if attr is not None and not isinstance(attr, list):
            return

        call_result = self._functionCall.exec(params)
        # Get the class of the range (to create a new instance or convert to the correct type)
        range_type = self._range.get()

        if call_result == None:
            return
        
        elif isinstance(self._subsuming_property, DLDatatypeProperty):
            # here the subsuming property is a datatype property

            # Cast value result as wanted type
            call_result = convert(range_type, call_result)

            # for non functional properties, we check if the value doesn't already exist
            # if it does, we don't add the assertion again
            if attr is not None and call_result in attr:
                return None
            
            assertions.append(DatatypePropertyAssertion(self._subsuming_property, instance, call_result))
        else:
            # here, the subsuming property is an object property

            # for non functional properties, we need to check if the instance doesn't already exist
            # (well it doesn't, but we'll check every associated datatype properties)
            if attr is not None and any([areEqual(c, call_result) for c in attr]):
                return None
            
            # creates the instance of the concept with a unique name
            c = ClassAssertion(range_type)
            new_inst = c.get_instance()
            if instances is not None:
                instances.append(new_inst)
            assertions.append(ObjectPropertyAssertion(self._subsuming_property, instance, new_inst))
            assertions.append(c)
            # "fill" the necessary properties of the new instance and add the associated assertions
            self.fillProperties(new_inst, call_result, assertions, instances)
    
    def fillProperties(self, instance, call_result, assertions, instances = None):

        for prop, isDatatype, value in call_result:

            # we get the range is specified
            # if not, and it is an object property, we'll create a Thing instance
            # if it is a datatype property, we'll take the result of the function without trying to convert
            prop_range_type = prop.get().range[0] if prop.get().range else None

            # if it is an object property
            # create the necessary instance and fill its properties recursively
            # then fill the object property
            if not isDatatype:
                # create the new instance for the object property
                c = ClassAssertion(prop_range_type)
                new_inst = c.get_instance()
                # save the new instance for future calls
                if instances is not None:
                    instances.append(new_inst)
                assertions.append(ObjectPropertyAssertion(prop, instance, new_inst))
                assertions.append(c)
                self.fillProperties(new_inst, value, assertions, instances)
            
            # if it is a datatype property
            else:
                d = None
                # if the datatype property is not functional (can have multiple values)
                # and the function returns all those values in a collection
                if isinstance(value, (list, tuple, set, dict)) and (type(value) is not str):
                    d = DatatypePropertyAssertion(prop, instance, [convert(prop_range_type, x) for x in value], True)
                else:
                    d = DatatypePropertyAssertion(prop, instance, convert(prop_range_type, value))
                assertions.append(d)

    def __repr__(self):
        return self.name