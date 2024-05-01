from lcall.DLClass import DLClass
from lcall.DLDatatype import DLDatatype
from lcall.DLDatatypeProperty import DLDatatypeProperty
from lcall.DLProperty import DLProperty
from lcall.DLInstance import DLInstance
from lcall.DLPropertyChain import DLPropertyChain
from lcall.classAssertion import ClassAssertion
from lcall.datatypePropertyAssertion import DatatypePropertyAssertion
from lcall.objectPropertyAssertion import ObjectPropertyAssertion
from lcall.callableThing import CallableThing
from lcall.DLPropertyChain import DLPropertyChain
from lcall.assertion import Assertion
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
    if type is bool: # not sure of that
        return type(value not in ("false", "False", "0", False, 0))
    else:
        return type(value)


class CallFormula:
    """
    Object representing a call formula
    """

    def __init__(self, name: str, subsuming_property: DLProperty, function: CallableThing, 
                 parameters: list[DLPropertyChain], call_domain: DLClass, call_range: (DLDatatype | DLClass)):
        """
        Create a call formula object from its function(s) (arbitrary), parameters, domain and datatype range

        :param name: the name of the call (instance)
        :param subsuming_property: the datatype property subsuming the call formula
        :param function: function(s) to be called
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
    
    def get_instances(self):
        return self._domain.get().instances()
    

    def add_assertion_if_not_new(self, value: Any, range_type: (type | None), current_values: Any, 
                                 instance: DLInstance, assertions: list[Assertion]) -> bool:
        """
        Add the datatype property assertion if the knowledge base doesn't entail the formula property(instance, value).
        In other words, value is not in {x | property(instance, x)}. This set is `current_values`.
        (property comes from the `add_datatype_property_assertion` method)

        :param value: the value to add
        :param range_type: the type of range of the property (to convert the value)
        :param current_values: the current values of the property for the instance `instance`
        :param instance: the instance of the assertion
        :param assertions: list of the new assertions(to complete)
        :return True if the assertion was created and added to assertions
        """
        value = convert_to(value, range_type)
        # if the assertion is new
        # if the current values are a list (non-functional property) we check if the value to add is not in the list
        # if the current values aren't a list (functional property) we check if the value isn't already the current value
        # we don't prevent the creation of inconsistencies (there will be signaled by the reasoner)
        if (isinstance(current_values, list) and value not in current_values) or (value is not current_values):
            assertions.append(DatatypePropertyAssertion(self._subsuming_property, instance, value))
            return True
        return False
    
        
    def add_datatype_property_assertion(self, value, range_type, property, instance, assertions):
        # we get the current property values of the instance
        current_values = getattr(instance.get(), property.get().name, None)
        # if there are mutliple elements
        if is_a_container(value):
            for res in value:
                # if you have nested list in the list of values, it is not taken into account
                if not is_a_container(res):
                    if self.add_assertion_if_not_new(res, range_type, current_values, instance, assertions):
                        # we update the current values if a value was added (for the possible next iteration)
                        # we could check if the current_values are a list or not and add/replace res but this is simpler
                        current_values = getattr(instance.get(), property.get().name, None)
        else:
            # Cast value result as wanted type
            self.add_assertion_if_not_new(value, range_type, current_values, instance, assertions)
            # we do not need to update the current values as they will not be used later


    def add_object_property_assertion(self, values, range_type, property, instance, assertions, instances):
        # creates the instance of the concept with a unique name
        c = ClassAssertion(range_type)
        new_inst = c.get_instance()
        # this is necessary because of the infer2_calls method in the infer.py
        if instances is not None:
            instances.append(new_inst)
        assertions.append(ObjectPropertyAssertion(property, instance, new_inst))
        assertions.append(c)
        # "fill" the necessary properties of the new instance and add the associated assertions
        self.fill_properties(new_inst, values, assertions, instances)

    def exec(self, instance: DLInstance, params: list, assertions, instances = None) -> None:
        """
        Execute the call formula calculation, create and update assertions

        :param instance: instance from which the parameters are derived
        :param params: parameter values to use
        :param assertions: the list current assertions to update
        :return true if new assertions were inferred
        """

        call_result = self._function.exec(params)
        # Get the class of the range (to create a new instance or convert to the correct type)
        range_type = self._range.get()

        if call_result == None:
            return
        elif isinstance(self._subsuming_property, DLDatatypeProperty):
            self.add_datatype_property_assertion(call_result, range_type, self._subsuming_property, instance, assertions)
        else:
            # there is no check if the assertion if new or not cause we create a new instance, so it's always a new assertion
            # the new instance could be the same as an already existing one but this will be inferred by the reasoner
            # and if there are inconsistencies in the properties of the instances supposed to be equal, it will also be signaled by the reasoner
            self.add_object_property_assertion(call_result, range_type, self._subsuming_property, instance, assertions, instances)
    
    
    def fill_properties(self, instance, call_result, assertions, instances = None):
        for property, isDatatype, value in call_result:
            range_type = property.get().range[0] if property.get().range else None
            if isDatatype:
                self.add_datatype_property_assertion(value, range_type, property, instance, assertions)
            else:
                self.add_object_property_assertion(value, range_type, property, instance, assertions, instances)
                

    def __repr__(self):
        return self.name