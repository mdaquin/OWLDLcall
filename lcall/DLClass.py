from abc import ABC, abstractmethod


class DLClass(ABC):
    """
    An object representing a class in description logics
    """

    @abstractmethod
    def get(self):
        """
        Gets the representation of the class

        :return: representation of the class
        """
        pass
