# ${\text{OWL~DL}}^{\fm{call}}$

OWL DL^call is an extension of OWL DL when call to external functions returning unique datatype values. It was developped in particular to enable combining description logic-based reasoning with symbolic computation and is illustrated on a simple example showing how an equation can be classified as being a second degree polynomial equation (or quadratic equation) through the interplay of the description logic reasoner (Hermit) and python code using the SimPy librabry.

The OWL DL^call code was originally contributed by @stlnb and is maintained by the K Team at the Loria laboratory in Nancy, France. 

## Requirements

OWL DL^call is developped using the OWLready2 library to handle OWL DL ontologies and description logic reasoning. In addition, it requires Python 3.9+. To ensure the relevant dependencies are installed, please run.

``
pip install -r requirements.txt
``

## Usage

`infer.py` is the main entry point to the inference engine. It takes two parameters :
 - The `directory` in which OWL files are localted, including the call.owl file as well as any owl files involved in the reasoning task to be carried out.
 - The `IRI of the main ontology` to use. The file for this ontology must be located in the directory provided, and might import other ontologies (including the call.owl).
It produces on the screen the triples that are generated from call to external functions.

## Example

The samples repository contains an ontology (equations.owl) using the call ontology (call.owl) that describes classes of equations (polynomial equations, quadratic equations, etc.) and three examples of equations to be classified. It includes two calls to functions written in python to recognise whether an equation is polynomial, and to compute the degree of a polynomial equation. 

To run the example, apply the command line: 

``
python infer.py samples/ 'https://k.loria.fr/ontologies/examples/equations'
``
This should produce the following output:
``
<https://k.loria.fr/ontologies/examples/equations#eq2> <https://k.loria.fr/ontologies/examples/equations#degree> "2" .
<https://k.loria.fr/ontologies/examples/equations#eq3> <https://k.loria.fr/ontologies/examples/equations#isAPolynomialEquation> "True" .
<https://k.loria.fr/ontologies/examples/equations#eq1> <https://k.loria.fr/ontologies/examples/equations#isAPolynomialEquation> "True" .
<https://k.loria.fr/ontologies/examples/equations#eq2> <https://k.loria.fr/ontologies/examples/equations#isAPolynomialEquation> "True" .
<https://k.loria.fr/ontologies/examples/equations#eq1> <https://k.loria.fr/ontologies/examples/equations#degree> "2" .
<https://k.loria.fr/ontologies/examples/equations#eq3> <https://k.loria.fr/ontologies/examples/equations#degree> "1" .
``

Therefore indiquating that all three equations are polynomial, that eq1 and eq2 are of degree 2 and that eq3 is of degree 1. Adding those triples to the ontology would therefore enable classifying eq1 and eq2 as quadratic equations.
