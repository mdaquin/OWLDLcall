from abc import ABC, abstractmethod


class DLDatatype(ABC):
    """
    An object representing a datatype in description logics
    """

    @abstractmethod
    def get(self):
        """
        Gets the representation of the datatype

        :return: representation of the datatype
        """
        pass
