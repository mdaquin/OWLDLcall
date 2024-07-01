import logging
import sys

from lcall.owlRdyReasoner import OwlRdyReasoner


def backward_infer(onto_iri: str, local_path: str, instance: str, _property: str):
    onto_loaded = None
    try:
        onto_loaded = OwlRdyReasoner(onto_iri, local_path)
    # if there is an unrecognized property name
    except AttributeError as e:
        logging.error(e)
        exit(-1)
    
    instance = getattr(onto_loaded.namespace, instance)
    if instance is None:
        logging.error(f"Instance '{instance}' not found.")
        return
    _property = getattr(onto_loaded.namespace, _property)
    if _property is None:
        logging.error(f"Property '{_property}' not found.")
        return
    return 3


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # 4 parameters
    # required : the path to directory containing ontologies, the IRI of the main ontology
    if len(sys.argv) != 5:
        logging.error("Usage: python lcall <path to directory containing ontologies> <IRI of main ontology> "
                      "<instance> <property>")
        exit(-1)

    res = backward_infer(sys.argv[2], sys.argv[1], sys.argv[3], sys.argv[4])
    if res:
        print(res)
    else:
        print("None found.")
