import owlready2 as owl

owl.onto_path.append("samples/")
onto = owl.get_ontology("https://k.loria.fr/ontologies/examples/equations").load()
# with onto:
#     owl.sync_reasoner(infer_property_values=True, debug=False)

call = owl.get_namespace("https://k.loria.fr/ontologies/call")

world = call.world

for x in world.sparql("""SELECT ?x ?y ?z { ?x ?y ?z . }"""):
    print(x)