from lcall.DLProperty import DLProperty


class DLPropertyChain:
    """
    An object representing a property chain
    """
    def __init__(self, properties: list[DLProperty]):
        """
        Initialization

        :param properties: list of object properties of the chain and the datatype property (at the end)
        """
        self.properties = properties

    def __repr__(self) -> str:
        return ";".join((str(x) for x in self.properties))

    def __iter__(self):
        return iter(self.properties)
    
    def get_datatype_property(self):
        return self.properties[0]
