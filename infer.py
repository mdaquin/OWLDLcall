import logging
import sys
import getopt

from lcall.DLInstance import DLInstance
from lcall.abstractReasoner import AbstractReasoner
from lcall.assertion import Assertion
from lcall.owlRdyReasoner import OwlRdyReasoner
from lcall.datatypePropertyAssertion import DatatypePropertyAssertion
from lcall.callFormula import CallFormula


def assertions_entailed_by_calls(onto_loaded: AbstractReasoner, individual: DLInstance, cache: dict,
                                 do_not_call: (dict[DLInstance, set[CallFormula]] | None)) -> list[Assertion]:
    """
    Infers assertions from the call formulas of the ontology for a given individual

    The ontology opened using the interface is updated with the assertions and these updates are persistent in the
    object kb_loaded

    :param onto_loaded: ontology loaded in the interface
    :param individual: individual of the ontology
    :param cache: cache for calls already executed
    :param do_not_call:
    :return: assertions inferred for the individual
    """
    assertions = []
    # the function gets the calls where the domain is a concept of the individual
    # we only keep calls that have not already been executed

    # AND calls that should not be called for ending purposes
    calls = (call for call in onto_loaded.calls_for_instance(individual) if (call, individual) not in cache and
             ((not do_not_call) or individual not in do_not_call or call not in do_not_call[individual]))

    for call in calls:
        new_assertions = []
        params_tuples = onto_loaded.list_val_params(individual, call.get_parameters())
        executed = False
        for params_tuple in params_tuples:
            executed = True
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
                    new_assertions.append(DatatypePropertyAssertion(call.get_subsuming_property(), individual, result))
            else:
                # we have to use the reasoner class to create instances
                new_instance = onto_loaded.add_object_prop_assertions(call, result, individual, new_assertions)
                if do_not_call:
                    # new instances can't be called on the calls that generated them to prevent infinite loops
                    do_not_call[new_instance] = {call}
                    if individual in do_not_call:
                        do_not_call[new_instance].update(do_not_call[individual])

        if executed:
            cache[call, individual] = new_assertions
            assertions.extend(new_assertions)
    return assertions


def infer_calls(onto_iri: str, local_path: str, filename: (str | None), ensure_end: bool) -> list[Assertion]:
    """
    Main algorithm making inferences on call formulas for the ontology

    Cycles through all instances and repeats until no more assertions are made.

    :param onto_iri: string of the ontology for the inference interface (usually an IRI)
    :param local_path: path to search ontology if using local files
    :param filename: the name of the file where will be saved the new assertions
    :param ensure_end:
    :return: list of all assertions inferred
    """
    # Change class with reasoner used (AbstractReasoner implementation)
    onto_loaded = None
    try:
        onto_loaded = OwlRdyReasoner(onto_iri, local_path, ensure_end)
    # if there is an unrecognized property name
    except AttributeError as e:
        logging.error(e)
        exit(-1)
        
    all_assertions = []
    # dict working as a cache for calls already executed
    cache = dict()
    # dict to prevent infinite loops
    do_not_call = dict() if ensure_end else None
    end = False
    
    while not end:
        temp = len(all_assertions)
        for i in onto_loaded.instances:
            all_assertions.extend(assertions_entailed_by_calls(onto_loaded, i, cache, do_not_call))
        # if no new assertions could be made, it's the end
        end = temp == len(all_assertions)
        # resync the reasoner
        if not onto_loaded.reason():
            logging.error("An inconsistency was found after adding some assertions. Execution stopped.")
            break
    
    # saves the new assertions on a file
    if filename:
        onto_loaded.onto.save(local_path + filename)
        logging.info(f"Saved in {local_path}{filename}")

    return all_assertions


if __name__ == "__main__":
    # 2 to 4 parameters
    # required : the path to directory containing ontologies, the IRI of the main ontology
    save_filename = None
    ensure_end = False
    log_level = logging.WARNING
    syntax = "Usage: python infer.py <path to directory containing ontologies> <IRI of main ontology> [-s <filename>]" \
             " [-e <T|F>] [-v].\n" + \
             "-s/--save : save the ontology with the new assertion in a file.\n-e/--ensure_end : if True (T), " \
             "ensure the end of the execution (but may generate less assertions).\n-v: Verbose."
    try:
        opts, args = getopt.getopt(sys.argv, "s:e:v", ["save=", "ensure_end=", "verbose"])
    except getopt.GetoptError:
        print("ERROR.", syntax)
        sys.exit(-1)

    if len(args) < 2:
        print("ERROR, missing required arguments.", syntax)
        exit(-1)
    for opt, arg in opts:
        if opt in ("-s", "--save"):
            save_filename = arg
        elif opt in ("-e", "--ensure_end"):
            ensure_end = True if arg == "T" or arg == "True" else False
        elif opt in ("-v", "--verbose"):
            log_level = logging.INFO
    
    logging.basicConfig(level=log_level)
    for t in infer_calls(args[2], args[1], save_filename, ensure_end):
        print(t)
