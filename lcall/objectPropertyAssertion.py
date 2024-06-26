from lcall.DLObjectProperty import DLObjectProperty
from lcall.DLInstance import DLInstance
from lcall.propertyAssertion import PropertyAssertion


class ObjectPropertyAssertion(PropertyAssertion):
    """
    An object representing an object assertion in description logics.
    This directly modifies the ontology by adding the assertion.
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
        # modifies the ontology
        self.object_property.get()[self.instance.get()].append(self.value.get())

    def get_property(self) -> DLObjectProperty:
        return self.get_object_property()
    
    def get_object_property(self) -> DLObjectProperty:
        return self.object_property

    def get_instance(self) -> DLInstance:
        return self.instance

    def get_value(self) -> DLInstance:
        return self.value

    def __repr__(self):
        return f'{self.instance} {self.object_property} "{self.value}" .'
