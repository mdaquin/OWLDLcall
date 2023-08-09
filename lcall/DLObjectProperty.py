from abc import ABC, abstractmethod


class DLObjectProperty(ABC):
    """
    An object representing an object property in description logics
    """

    @abstractmethod
    def get(self):
        """
        Gets the representation of the object property

        :return: representation of the object property
        """
        pass
