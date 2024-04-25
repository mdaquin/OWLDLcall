from abc import ABC, abstractmethod


class DLInstance(ABC):
    """
    An object representing an instance in description logics
    """

    @abstractmethod
    def get(self):
        """
        Gets the representation of the instance

        :return: representation of the instance
        """
        pass

    @abstractmethod
    def getName(self):
        """
        Gets the (unique) name of the instance

        :return: name of the instance
        """
        pass
