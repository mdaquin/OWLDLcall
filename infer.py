import logging
import sys

from lcall.DLInstance import DLInstance
from lcall.abstractReasoner import AbstractReasoner
from lcall.propertyAssertion import PropertyAssertion

from lcall.owlRdyReasoner import OwlRdyReasoner

def assertions_entailed_by_calls(onto_loaded: AbstractReasoner, individual: DLInstance, cache: dict) -> set[PropertyAssertion]:
    """
    Infers assertions from the call formulas of the ontology for a given individual

    The ontology opened using the interface is updated with the assertions and these updates are persistent in the
    object kb_loaded

    :param onto_loaded: ontology loaded in the interface
    :param individual: individual of the ontology
    :param cache: cache for calls already executed
    :return: assertions inferred for the individual
    """
    assertions = set()
    calls = onto_loaded.calls_for_instance(individual)
    for call in calls:
        new_assertions = set()
        if (call, individual) not in cache:
            params_tuples = onto_loaded.list_val_params(individual, call.get_parameters())
            for params_tuple in params_tuples:
                call_assertion = call.exec(individual, params_tuple)
                if call_assertion is not None:
                    if not onto_loaded.is_asserted(call_assertion):
                        new_assertions.add(call_assertion)

                if len(new_assertions) != 0:
                    assertions.update(new_assertions)
                    onto_loaded.add_assertions(new_assertions)

                cache[call, individual] = new_assertions    # NOTE: Prevents new executions of calls if failed
    return assertions


def infer_calls(onto_iri: str, local_path: str, save: bool):
    """
    Main algorithm making inferences on call formulas for the ontology

    Cycles through all instances and repeats until no more assertions are made.

    :param onto_iri: string of the ontology for the inference interface (usually an IRI)
    :param local_path: path to search ontology if using local files
    :return: set of all assertions inferred for the
    """
    # Change class with reasoner used (AbstractReasoner implementation)
    onto_loaded = OwlRdyReasoner(onto_iri, local_path)
    instances = onto_loaded.instances()
    # Dictionary working as a cache for calls
    cache = dict()
    all_assertions = set()
    a = "This is a placeholder to be able to enter the loop"
    while len(a) != 0:
        a = set()
        for i in instances:
            a.update(assertions_entailed_by_calls(onto_loaded, i, cache))
        all_assertions.update(a)
    if save:
        onto_loaded.onto.save(local_path+"equationsInferred.rdf")
        print("Saved in "+local_path+"equationsInferred.rdf")
    return all_assertions

if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO)
    logging.basicConfig(level=logging.ERROR)    
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        logging.error("Usage: python lcall <path to directory containing ontologies> <IRI of main ontology> [<T|F>: T if you want the new ontology (with the inferred knowledge to be saved (in samples/equationsInferred.rdf))]")
        exit(-1)
    for t in infer_calls(sys.argv[2], sys.argv[1], len(sys.argv) == 4 and sys.argv[3].lower() == "t"):
        print(t, end="")
