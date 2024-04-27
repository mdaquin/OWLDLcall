from abc import ABC, abstractmethod
from lcall.DLPropertyChain import DLPropertyChain

class FunctionCall(ABC):

    @abstractmethod
    def get_parameters(self) -> list[DLPropertyChain]:
        pass