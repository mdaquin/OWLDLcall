from lcall.DLDatatypeProperty import DLDatatypeProperty
from lcall.DLInstance import DLInstance
from lcall.propertyAssertion import PropertyAssertion


class DatatypePropertyAssertion(PropertyAssertion):
    """
    An object representing a datatype assertion in description logics
    """

    def __init__(self, datatype_property: DLDatatypeProperty, instance: DLInstance, value, multiple = False):
        """
        Initialization

        :param datatype_property: datatype property of this assertion
        :param instance: instance of this assertion
        :param value: datatype value of this assertion
        """
        self.datatype_property = datatype_property
        self.instance = instance
        self.value = value
        # WARNING, if you intend to use this class, this crates the datatype property of the instance
        if multiple:
            self.datatype_property.get()[self.instance.get()].extend(self.value)
        else:
            self.datatype_property.get()[self.instance.get()].append(self.value)

    def get_property(self) -> DLDatatypeProperty:
        return self.get_datatype_property()
    
    def get_datatype_property(self) -> DLDatatypeProperty:
        return self.datatype_property

    def get_instance(self) -> DLInstance:
        return self.instance

    def get_value(self):
        return self.value

    def __repr__(self):
        return f'{self.instance} <{self.datatype_property}> "{self.value}" .'
