# OWL DL<sup>call</sup>

$\text{OWL~DL}^{\text{call}}$ is an extension of OWL DL enabling calls to external functions returning unique datatype values during inference. It was developped in particular to enable combining description logic-based reasoning with symbolic computation and is illustrated on a simple example showing how an equation can be classified as being a second degree polynomial equation (or quadratic equation) through the interplay of the description logic reasoner (Hermit) and python code using the [SimPy](https://www.sympy.org/) library.

The $\text{OWL~DL}^{\text{call}}$ code was originally contributed by [@stlnb](https://github.com/stlnb/) and is maintained by the [K Team](https://k.loria.fr) at the [Loria](https://www.loria.fr) laboratory in Nancy, France. 

## Requirements

$\text{OWL~DL}^{\text{call}}$ is developped using the [OWLready2]([url](https://owlready2.readthedocs.io/en/v0.42/)) library to handle OWL DL ontologies and description logic reasoning. In addition, it requires Python 3.9+. To ensure that the relevant dependencies are installed, please run.

``
pip install -r requirements.txt
``

## Usage

`infer.py` is the main entry point to the inference engine. It takes two required parameters :
 - The `directory` in which OWL files are localted, including the `call.owl` file as well as any OWL file involved in the reasoning task to be carried out.
 - The `IRI of the main ontology` to use. The file for this ontology must be located in the directory provided, and might import other ontologies (including `call.owl`).

And three optional ones :
 - A `namefile` where the new ontology will be saved (under the directory provided in the first argument) if you want to save the ontology with the inferred assertions in a new file
 - A `ensure_end` option, if True, ensures the end of the execution (but may generate less assertions).
 - A `verbose` option.

It produces on `stdout` the triples (in NTriples format) that are generated from calls to external functions.


`lazy_infer.py` uses the same engine but reduces the scope to find a value to a given property of a given instance. As such, it takes 2 additional required parameters : the `property` and the `instance`.

## Example

The `samples` repository contains an ontology (`equations.owl`), using the call ontology (`call.owl`), that describes classes of equations (polynomial equations, quadratic equations, etc.), polynomial and matrices. It contains three examples of equations to be classified and one example of a square matrix from which we want to find the eigen values. It includes definitions of calls to functions written in python to recognise whether an equation is polynomial,compute the degree of a polynomial equation, find solutions of a quadratic equation, roots of a quadratic polynomial and eigen values of 2x2 matrices. 

To run the example, apply the command line: 

``
python infer.py samples/ 'https://k.loria.fr/ontologies/examples/equations'
``

It should output this :
```
eq1 <isAPolynomialEquation> "True" .
eq2 <isAPolynomialEquation> "True" .
eq3 <isAPolynomialEquation> "True" .
pb3 <hasSubProblem> findingroots1 .
findingroots1 <rdf:type> FindingRoots.
findingroots1 <hasPolynomial> polynomial1 .
polynomial1 <rdf:type> Polynomial.
polynomial1 <hasExpression> "X**2 - 4*X + 3" .
findingroots1 <hasSubProblem> equationsolving1 .
equationsolving1 <rdf:type> EquationSolving.
equationsolving1 <hasEquation> polynomialequation1 .
polynomialequation1 <rdf:type> PolynomialEquation.
polynomialequation1 <hasEquality> "X**2 - 4*X + 3 = 0" .
polynomialequation1 <hasUnknown> unknown1 .
unknown1 <rdf:type> Unknown.
unknown1 <hasName> "X" .
unknown1 <hasType> "real" .
polynomialequation1 <degree> "2" .
polynomialequation1 <isAPolynomialEquation> "True" .
eq1 <degree> "2" .
eq2 <degree> "2" .
eq3 <degree> "1" .
equationsolving1 <hasSolution> solutionset1 .
solutionset1 <rdf:type> SolutionSet.
solutionset1 <hasValue> "{1, 3}" .
equationsolving1 <hasSolution> solutionset2 .
solutionset2 <rdf:type> SolutionSet.
solutionset2 <hasValue> "{1, 3}" .
pb1 <hasSolution> solutionset3 .
solutionset3 <rdf:type> SolutionSet.
solutionset3 <hasValue> "{-2, -1}" .
pb1 <hasSolution> solutionset4 .
solutionset4 <rdf:type> SolutionSet.
solutionset4 <hasValue> "{-2, -1}" .
pb2 <hasSolution> solutionset5 .
solutionset5 <rdf:type> SolutionSet.
solutionset5 <hasValue> "{-2 - sqrt(3), -2 + sqrt(3)}" .
```

The program found that the 3 equations were polynomial equations, 2 of them were quadratic equations and the last one was a linear equation. It also found the solutions to the quadratic equations (solutionset1/solutionset2 and solutionset3/solutionset4) and the eigen values of the matrix (soltuionset5).
