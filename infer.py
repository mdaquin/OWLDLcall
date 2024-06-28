import logging
import sys

from lcall.DLInstance import DLInstance
from lcall.abstractReasoner import AbstractReasoner
from lcall.assertion import Assertion
from lcall.owlRdyReasoner import OwlRdyReasoner
from lcall.datatypePropertyAssertion import DatatypePropertyAssertion


def assertions_entailed_by_calls(onto_loaded: AbstractReasoner, individual: DLInstance, cache: set) -> list[Assertion]:
    """
    Infers assertions from the call formulas of the ontology for a given individual

    The ontology opened using the interface is updated with the assertions and these updates are persistent in the
    object kb_loaded

    :param onto_loaded: ontology loaded in the interface
    :param individual: individual of the ontology
    :param cache: cache for calls already executed
    :return: assertions inferred for the individual
    """
    assertions = []
    # the function gets the calls where the domain is a concept of the individual
    # we only keep calls that have not already been executed
    calls = (call for call in onto_loaded.calls_for_instance(individual) if (call, individual) not in cache)

    for call in calls:
        params_tuples = onto_loaded.list_val_params(individual, call.get_parameters())
        for params_tuple in params_tuples:
            # get the result of the function
            result = call.exec(params_tuple)
            # avoid indenting too much
            if result is None:
                continue
            # if the call subsuming property is a datatype one
            if call.is_a_datatype_call():
                # we check if the assertion isn't already entailed by the ontology
                current_values = call.get_subsuming_property().get()[individual.get()]
                if result not in current_values:
                    # creating the assertion object directly modifies the ontology
                    assertions.append(DatatypePropertyAssertion(call.get_subsuming_property(), individual, result))
            else:
                # we have to use the reasoner class ot create instances
                new_instances = onto_loaded.add_object_prop_assertions(call, result, individual, assertions)
                for new_instance in new_instances:
                    onto_loaded.instances.append(new_instance)
                    # new instances can't be called on the calls that generated them to prevent infinite loops
                    cache.add((call, new_instance))
            cache.add((call, individual))
    return assertions


def infer_calls(onto_iri: str, local_path: str, save_filename: (str | None)) -> list[Assertion]:
    """
    Main algorithm making inferences on call formulas for the ontology

    Cycles through all instances and repeats until no more assertions are made.

    :param onto_iri: string of the ontology for the inference interface (usually an IRI)
    :param local_path: path to search ontology if using local files
    :param savefilename : the name of the file where will be saved the new assertions
    :return: list of all assertions inferred
    """
    # Change class with reasoner used (AbstractReasoner implementation)
    try:
        onto_loaded = OwlRdyReasoner(onto_iri, local_path)
    # if there is an unrecognized property name
    except AttributeError as e:
        logging.error(e)
        exit(-1)

    all_assertions = []
    # set working as a cache for calls
    cache = set()
    end = False
    
    while not end:
        temp = len(all_assertions)

        for i in onto_loaded.instances:
            all_assertions.extend(assertions_entailed_by_calls(onto_loaded, i, cache))

        # if no new assertions could be made, it's the end
        end = temp == len(all_assertions)
        # resync the reasoner
        if not onto_loaded.reason():
            logging.error("An inconsistency was found after adding some assertions. Execution stopped.")
            break
    
    # saves the new assertions on a file
    if save_filename:
        onto_loaded.onto.save(local_path+save_filename)
        print("Saved in "+local_path+save_filename)

    return all_assertions


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # 2 or 3 parameters
    # required : the path to directory containing ontologies, the IRI of the main ontology
    # optional : the filename where to save the ontology with the new assertions (saved under the directory provided by the first argument)
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        logging.error("Usage: python lcall <path to directory containing ontologies> <IRI of main ontology> [<filename where to save the changes>]")
        exit(-1)
    
    # file where to save the changes to the ontology
    save_filename = None if len(sys.argv) == 3 else sys.argv[3]

    for t in infer_calls(sys.argv[2], sys.argv[1], save_filename):
        print(t)
