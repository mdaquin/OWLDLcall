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
    if type is bool: # not sure about that
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
        

    def add_datatype_property_assertion(self, value: Any, range_type: (type | None), property: DLDatatypeProperty, 
                                        instance: DLInstance, assertions: list[Assertion]) -> None:
        """
        Add the datatype property assertion if the knowledge base B doesn't entail the assertion `property(instance, value)`.
        In other words, if `value` is not in `{x | B entails property(instance, x)}`.

        :param value: the resul of the function, the value to add (can be multiple values)
        :param range_type: the range of the property (to convert the value(s))
        :param property: the property of the assertion
        :param instance: the instance
        :param assertions: the list of new assertions (to complete)
        """
        # if there are mutliple elements
        # datatype properties can't be containers but if the property isn't functional,
        # a function could return several values of the property
        if is_a_container(value):
            for res in value:
                self.add_datatype_property_assertion(res, range_type, property, instance, assertions)
        else:
            # current values of the property and instances to know if the value we want to add is already asserted
            current_values = property.get()[instance.get()]
            value = convert_to(value, range_type)
            # if value isn't already in the current values
            # we don't prevent the creation of inconsistencies (there will be signaled by the reasoner)
            if value not in current_values:
                assertions.append(DatatypePropertyAssertion(property, instance, value))


    def add_object_property_assertion(self, values: list[tuple[DLProperty, (DLClass | DLDatatype), Any]], range_type: (type | None), 
                                      property: DLProperty, instance: DLInstance, assertions: list[Assertion], 
                                      instances: (list[DLInstance] | None)) -> None:
        """
        Create an instance (and its properties) and add the object property assertion
        the new instance could be the same as an already existing one but this will be inferred by the reasoner

        :param values: the resul of the functions as a list of triples
        :param range_type: the range of the property (to create the instance of the right class)
        :param property: the property of the assertion
        :param instance: the instance
        :param assertions: the list of new assertions (to complete)
        :param instances: the list of existing instances (to complete)
        """
        # creates the instance of the concept with a unique name
        c = ClassAssertion(range_type)
        new_inst = c.get_instance()
        # this is necessary because of the infer2_calls method in the infer.py
        if instances is not None:
            instances.append(new_inst)
        assertions.append(ObjectPropertyAssertion(property, instance, new_inst))
        assertions.append(c)
        # "fill" the necessary properties of the new instance and add the associated assertions
        for new_property, range, value in values:
            if isinstance(range, DLDatatype):
                self.add_datatype_property_assertion(value, range.get(), new_property, 
                                                     new_inst, assertions)
            else:
                self.add_object_property_assertion(value, range.get(), new_property, 
                                                   new_inst, assertions, instances)


    def exec(self, instance: DLInstance, params: list[DLPropertyChain], 
             assertions: list[Assertion], instances: (list[DLInstance] | None) = None) -> None:
        """
        Execute the call formula calculation, create and update assertions if necessary

        :param instance: instance from which the parameters are derived
        :param params: parameter values to use
        :param assertions: the list of new assertions (to update)
        :param instances: the list of all instances 
        (object property assertions create instances so we add them to the list of instances)
        """

        call_result = self._function.exec(params)
        # Get the class of the range (to create a new instance or convert to the correct type)
        range_type = self._range.get()

        if call_result == None:
            return
        elif isinstance(self._subsuming_property, DLDatatypeProperty):
            self.add_datatype_property_assertion(call_result, range_type, self._subsuming_property, instance, assertions)
        else:
            self.add_object_property_assertion(call_result, range_type, self._subsuming_property, instance, assertions, instances)
                

    def __repr__(self):
        return self.name