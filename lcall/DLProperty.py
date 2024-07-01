from abc import ABC, abstractmethod


class DLProperty(ABC):
    """
    An object representing a property in description logics
    """

    @abstractmethod
    def get(self):
        """
        Gets the representation of the property

        :return: representation of the property
        """
        pass
