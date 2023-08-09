from abc import ABC, abstractmethod


class DLDatatypeProperty(ABC):
    """
    An object representing a datatype property in description logics
    """

    @abstractmethod
    def get(self):
        """
        Gets the representation of the datatype property

        :return: representation of the datatype property
        """
        pass
