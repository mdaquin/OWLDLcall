from lcall.DLDatatypeProperty import DLDatatypeProperty
from lcall.DLObjectProperty import DLObjectProperty


class DLPropertyChain:
    """
    An object representing a property chain
    """
    def __init__(self, datatype_property: DLDatatypeProperty, *object_properties: DLObjectProperty):
        """
        Initialization

        :param datatype_property: datatype property at the end of the chain
        :param object_properties: list of object properties of the chain
        """
        self.datatype_property = datatype_property
        self.object_property_list = list(object_properties)

    def __repr__(self):
        disp = "["
        for obj_prop in self.object_property_list:
            disp += str(obj_prop) + ", "
        disp += str(self.datatype_property) + "]"
        return disp

    def __iter__(self):
        res = []
        res.extend(self.object_property_list)
        res.append(self.datatype_property)
        return res.__iter__()
