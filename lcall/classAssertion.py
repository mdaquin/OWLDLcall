from lcall.DLClass import DLClass
from lcall.assertion import Assertion
from lcall.DLInstance import DLInstance


class ClassAssertion(Assertion):
    """
    An object representing a class assertion in description logics.
    Unlike other assertions classes, thi class does not modify the ontology.
    Creating an instance or adding a class to a instance should be done before creating this object.
    """

    def __init__(self, concept: DLClass, instance: DLInstance):
        """
        Initialization.

        :param concept: the concept of the assertion
        :param instance: the instance of the assertion
        """
        self.concept = concept
        self.instance = instance

    def get_concept(self) -> DLClass:
        return self.concept
    
    def get_instance(self) -> DLInstance:
        return self.instance

    def __repr__(self):
        return f'{self.instance} <rdf:type> {self.concept}.'
