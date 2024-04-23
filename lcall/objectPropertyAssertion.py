from lcall.DLObjectProperty import DLObjectProperty
from lcall.DLInstance import DLInstance
from lcall.propertyAssertion import PropertyAssertion


class ObjectPropertyAssertion(PropertyAssertion):
    """
    An object representing an object assertion in description logics
    """

    def __init__(self, object_property: DLObjectProperty, instance: DLInstance, value: DLInstance):
        """
        Initialization

        :param object_property: object property of this assertion
        :param instance: instance of this assertion
        :param value: instance value of this assertion
        """
        self.object_property = object_property
        self.instance = instance
        self.value = value

    def get_property(self) -> DLObjectProperty:
        return self.get_object_property()
    
    def get_object_property(self) -> DLObjectProperty:
        return self.object_property

    def get_instance(self) -> DLInstance:
        return self.instance

    def get_value(self) -> DLInstance:
        return self.value

    def __repr__(self):
        # return str(self.datatype_property) + "(" + str(self.instance) + ", " + str(self.value) + ")"
        return f'{self.instance} {self.object_property} "{self.value}" .\n'
