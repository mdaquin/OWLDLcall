import logging
import sys
from owlready2 import OwlReadyInconsistentOntologyError

from lcall.DLInstance import DLInstance
from lcall.abstractReasoner import AbstractReasoner
from lcall.propertyAssertion import PropertyAssertion
from lcall.owlRdyInstance import OwlRdyInstance
from lcall.assertion import Assertion
from lcall.owlRdyReasoner import OwlRdyReasoner

def assertions_entailed_by_calls(onto_loaded: AbstractReasoner, individual: DLInstance, cache: dict, instances: list[DLInstance]) -> set[PropertyAssertion]:
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
    calls = onto_loaded.calls_for_instance(individual)
    for call in calls:
        if (call, individual) not in cache:
            params_tuples = onto_loaded.list_val_params(individual, call.get_parameters())
            for params_tuple in params_tuples:
                call.exec(individual, params_tuple, assertions, instances)
                # we don't need to save anything
            cache[call, individual] = assertions   # NOTE: Prevents new executions of calls if failed
    return assertions


def infer_calls(onto_iri: str, local_path: str, savefilename: str) -> list[Assertion]:
    """
    Main algorithm making inferences on call formulas for the ontology

    Cycles through all instances and repeats until no more assertions are made.

    :param onto_iri: string of the ontology for the inference interface (usually an IRI)
    :param local_path: path to search ontology if using local files
    :param savefilename : the file where will be saved the new assertions
    :return: list of all assertions inferred
    """
    # Change class with reasoner used (AbstractReasoner implementation)
    onto_loaded = OwlRdyReasoner(onto_iri, local_path)
    # Dictionary working as a cache for calls
    cache = dict()
    # assertions
    all_assertions = []
    instances = onto_loaded.instances()
    end = False

    while not end:
        temp = len(all_assertions)
        for i in instances:
            all_assertions.extend(assertions_entailed_by_calls(onto_loaded, i, cache, instances))
        # if no new assertions could be made, it's the end
        end = temp == len(all_assertions)
        # I believe you can sync the reasoner as late as here
        try:
            onto_loaded.reason()
        except OwlReadyInconsistentOntologyError:
            logging.error("Incohérence détectée. Assertions réalisées :")
            for assertion in all_assertions:
                logging.info(assertion)
            if savefilename != "":
                onto_loaded.onto.save(local_path+savefilename)
                print("Saved in "+local_path+savefilename)
            exit(-1)
    
    # saves the new assertions on a new file
    if savefilename != "":
        onto_loaded.onto.save(local_path+savefilename)
        print("Saved in "+local_path+savefilename)

    return all_assertions


def infer2_calls(onto_iri: str, local_path: str, savefilename: str) -> list[Assertion]:
    """
    Main algorithm making inferences on call formulas for the ontology

    Cycles through *all calls* and repeats until no more assertions are made.

    :param onto_iri: string of the ontology for the inference interface (usually an IRI)
    :param local_path: path to search ontology if using local files
    :param savefilename : the file where will be saved the new assertions
    :return: list of all assertions inferred
    """

    # Change class with reasoner used (AbstractReasoner implementation)
    onto_loaded = OwlRdyReasoner(onto_iri, local_path)
    # Dictionary working as a cache for calls
    cache = set()
    # assertions
    all_assertions = []
    end = False
    while not end:
        temp = len(all_assertions)
        for call in onto_loaded.calls:
            for i in call.get_instances():
                
                if (call, i) not in cache:
                    individual = OwlRdyInstance(i)
                    params_tuples = onto_loaded.list_val_params(individual, call.get_parameters())
                    for params_tuple in params_tuples:
                        call.exec(individual, params_tuple, all_assertions)
                        # we don't need to save anything
                        cache.add((call, i))

        # if no new assertions could be made, it's the end
        end = temp == len(all_assertions)
        # I believe you can sync the reasoner as late as here
        try:
            onto_loaded.reason()
        except OwlReadyInconsistentOntologyError:
            logging.error("Incohérence détectée. Assertions réalisées :")
            for assertion in all_assertions:
                logging.error(assertion)
            exit(-1)
    # saves the new assertions on a new file
    if savefilename != "":
        onto_loaded.onto.save(local_path+savefilename)
        print("Saved in "+local_path+savefilename)
    return all_assertions

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # 2 or 3 parameters
    # required : the path to directory containing ontologies, the IRI of the main ontology
    # optional : the filename where to save the ontology with the new assertions (saved under the directory provided by the first argument)
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        logging.error("Usage: python lcall <path to directory containing ontologies> <IRI of main ontology> [<filename where to save the changes>]")
        exit(-1)
    for t in infer_calls(sys.argv[2], sys.argv[1], "" if len(sys.argv) == 3 else sys.argv[3]):
        print(t)
