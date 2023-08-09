from abc import ABC, abstractmethod


class CallableThing(ABC):
    """
    An object representing something the program can make a call upon (function, http request, ...)
    """
    @abstractmethod
    def exec(self, params: list):
        """
        Execute the call

        :param params: parameter values to use
        :return: result of the execution of the call
        """
        pass
