import logging
import sys
import getopt
from owlready2 import ObjectPropertyClass, NamedIndividual

from lcall.DLInstance import DLInstance
from lcall.abstractReasoner import AbstractReasoner
from lcall.assertion import Assertion
from lcall.owlRdyReasoner import OwlRdyReasoner
from lcall.datatypePropertyAssertion import DatatypePropertyAssertion
from lcall.callFormula import CallFormula
from lcall.owlRdyInstance import OwlRdyInstance


def assertions_entailed_by_calls(onto_loaded: AbstractReasoner, individual: DLInstance, cache: dict,
                                 instances: list[DLInstance],
                                 do_not_call: (dict[DLInstance, set[CallFormula]] | None)) -> list[Assertion]:
    """
    Infers assertions from the call formulas of the ontology for a given individual

    The ontology opened using the interface is updated with the assertions and these updates are persistent in the
    object kb_loaded

    :param onto_loaded: ontology loaded in the interface
    :param individual: individual of the ontology
    :param cache: cache for calls already executed
    :param instances: the list of instances to update in case new instances are created
    :param do_not_call: a dictionary to prevent certain calls that might cause infinite loops 
    (or None if we don't ensure the end)
    :return: assertions inferred for the individual
    """
    assertions = []
    # the function gets the calls where the domain is a concept of the individual
    # we only keep calls that have not already been executed
    # AND calls that should not be called for ending purposes
    calls = (call for call in onto_loaded.calls_for_instance(individual)
             if (call, individual) not in cache and (not do_not_call or (individual not in do_not_call
                                                                         or call not in do_not_call[individual])))

    for call in calls:
        params_tuples = onto_loaded.list_val_params(individual, call.get_parameters())
        executed = False
        new_assertions = []
        for params_tuple in params_tuples:
            executed = True
            # get the result of the function
            results = call.exec(params_tuple)
            if results is None:
                continue
            # if the call subsuming property is a datatype one
            if call.is_a_datatype_call():
                # we check if the assertion isn't already entailed by the ontology
                current_values = call.get_subsuming_property().get()[individual.get()]
                for result in results:
                    if result not in current_values:
                        # creating the assertion object directly modifies the ontology
                        new_assertions.append(DatatypePropertyAssertion(call.get_subsuming_property(),
                                                                        individual, result))
            else:
                # we have to use the reasoner class ot create instances
                new_instances = onto_loaded.add_assertions(results, call.get_subsuming_property(), call.get_range(),
                                                           call.get_result_list(), individual, new_assertions)
                for new_instance in new_instances:
                    instances.append(new_instance)
                    if do_not_call:
                        # new instances can't be called on the calls that generated them to prevent infinite loops
                        do_not_call[new_instance] = {call}
                        if individual in do_not_call:
                            do_not_call[new_instance].update(do_not_call[individual])

        if executed:
            cache[call, individual] = new_assertions
            assertions.extend(new_assertions)
    return assertions


def get_relevant_instances(instance: NamedIndividual, relevant_instances: set[NamedIndividual]):
    """
    Get relevant instances.
    From an instance x, add all instances y such that there exists a property p with p(x, y) or p(y, x)
    Recusrively add the relevant instances from y.
    """
    relevant_instances.add(instance)
    for prop in instance.INDIRECT_get_properties():
        if isinstance(prop, ObjectPropertyClass):
            for value in prop[instance]:
                if value not in relevant_instances:
                    get_relevant_instances(value, relevant_instances)
    for ins, _ in instance.get_inverse_properties():
        if ins not in relevant_instances:
            get_relevant_instances(ins, relevant_instances)


def not_really_lazy_infer(onto_iri: str, local_path: str, instance: str, _property: str, 
                          filename: (str | None), ensure_end: bool) -> list:
    """
    Algorithm making inferences on call formulas for the ontology

    Cycles through *relevant* instances and repeats until no more assertions are made 
    or a value to the property is found.

    :param onto_iri: string of the ontology for the inference interface (usually an IRI)
    :param local_path: path to search ontology if using local files
    :param instance: the instance
    :param _property: the property to find
    :param filename: the name of the file where will be saved the new assertions
    :param ensure_end: option to ensure the execution ends
    :return: a list of the values found (such that for a value `v`, `_property(instance, v)`)
    """
    onto_loaded = None
    try:
        onto_loaded = OwlRdyReasoner(onto_iri, local_path)
    # if there is an unrecognized property name
    except AttributeError as e:
        logging.error(e)
        exit(-1)

    # get the instance from the string
    instance = getattr(onto_loaded.onto, instance)
    if instance is None:
        logging.error(f"Instance '{instance}' not found.")
        return
    instance = OwlRdyInstance(instance)

    # get the property from the string
    owl_property = getattr(onto_loaded.onto, _property)
    if owl_property is None:
        logging.error(f"Property '{_property}' not found.")
        return
    
    # if there is aleady a value
    if owl_property[instance.get()]:
        return owl_property[instance.get()]

    all_assertions = []
    # get the relevant instances
    # basically the instance in parameters and associated instances with object properties
    instances = set()
    get_relevant_instances(instance.get(), instances)
    instances = [OwlRdyInstance(x) for x in instances]
    # dict working as a cache for calls already executed
    cache = dict()
    # dict to prevent infinite loops
    do_not_call =  dict() if ensure_end else None
    end = False

    while not end:
        temp = len(all_assertions)

        for i in instances:
            all_assertions.extend(assertions_entailed_by_calls(onto_loaded, i, cache, instances, do_not_call))

        # sync the reasoner
        if not onto_loaded.reason():
            logging.error("An inconsistency was found after adding some assertions. Execution stopped.")
            break

        # if no new assertions could be made or we found the value we wanted, it's the end
        end = temp == len(all_assertions) or owl_property[instance.get()]

    logging.info("Added assertions :")
    for x in all_assertions:
        logging.info(f"    {x}")

    # saves the new assertions on a file
    if filename:
        onto_loaded.onto.save(local_path + filename)
        print("Saved in " + local_path + filename)
    return owl_property[instance.get()]
    

if __name__ == "__main__":
    # save the ontology with the new assertions
    save_filename = None
    # ensure the end of the execution by preventing some calls to be checked
    _ensure_end = True
    log_level = logging.WARNING

    syntax = "Usage: python infer.py <path to directory containing ontologies> <IRI of main ontology> <instance> <property> [-s <filename>]" \
             " [-e <T|F>] [-v].\n" + \
             "-s/--save : save the ontology with the new assertion in a file.\n" + \
             "-e/--ensure_end : if True (T), ensure the end of the execution (but may generate less assertions).\n" + \
             "-v/--verbose : verbose."
    
    # four required arguments
    if len(sys.argv) < 5:
        print("ERROR, missing required arguments.\n", syntax)
        exit(-1)
    # find the optional arguments
    try:
        opts, _ = getopt.getopt(sys.argv[5:], "s:e:v", ["save=", "ensure_end=", "verbose"])
    except getopt.GetoptError:
        print("ERROR.", syntax)
        sys.exit(-1)

    for opt, arg in opts:
        if opt in ("-s", "--save"):
            save_filename = arg
        elif opt in ("-e", "--ensure_end"):
            _ensure_end = False if arg.lower() not in ("t", "true") else True
        elif opt in ("-v", "--verbose"):
            log_level = logging.INFO

    logging.basicConfig(level=log_level)
    # the (not so) lazy algorithm 
    # basically, the infer.py file but the scope of instances treated is reduced to relevant ones
    res = not_really_lazy_infer(sys.argv[2], sys.argv[1], sys.argv[3], sys.argv[4], save_filename, _ensure_end)
    print(res if res else "None found.")
