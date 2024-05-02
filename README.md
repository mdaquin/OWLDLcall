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

And an optional one :
 - A `namefile` where the new ontology will be saved (under the directory provided in the first argument) if you want to save the inferred assertions in a new file

It produces on `stdout` the triples (in NTriples format) that are generated from calls to external functions. (not accurate)

## Example

The `samples` repository contains an ontology (`equations.owl`), using the call ontology (`call.owl`), that describes classes of equations (polynomial equations, quadratic equations, etc.) and three examples of equations to be classified. It includes two definitions of calls to functions written in python to recognise whether an equation is polynomial and to compute the degree of a polynomial equation. 

To run the example, apply the command line: 

``
python infer.py samples/ 'https://k.loria.fr/ontologies/examples/equations'
``

It should output this :
```
eq1 <isAPolynomialEquation> "True" .
eq2 <isAPolynomialEquation> "True" .
eq3 <isAPolynomialEquation> "True" .
mat1 <isASquareMatrix> "True" .
mat2 <isASquareMatrix> "True" .
mat3 <isASquareMatrix> "False" .
pb3 <hasSubProblem> "equationsolving1" .
equations.EquationSolving(equationsolving1) .
equationsolving1 <hasEquation> "equation1" .
equations.Equation(equation1) .
equation1 <hasEquality> "t**2 - 4*t + 3 = 0" .
equation1 <hasUnknown> "unknown1" .
equations.Unknown(unknown1) .
unknown1 <hasName> "t" .
unknown1 <hasType> "real" .
eq1 <degree> "2" .
eq2 <degree> "2" .
eq3 <degree> "1" .
equation1 <isAPolynomialEquation> "True" .
pb1 <hasSolution> "solutionset1" .
equations.SolutionSet(solutionset1) .
solutionset1 <hasValue> "-2" .
solutionset1 <hasValue> "-1" .
pb1 <hasSolution> "solutionset2" .
equations.SolutionSet(solutionset2) .
solutionset2 <hasValue> "-1" .
solutionset2 <hasValue> "-2" .
pb2 <hasSolution> "solutionset3" .
equations.SolutionSet(solutionset3) .
solutionset3 <hasValue> "-2 - sqrt(3)" .
solutionset3 <hasValue> "-2 + sqrt(3)" .
equation1 <degree> "2" .
equationsolving1 <hasSolution> "solutionset4" .
equations.SolutionSet(solutionset4) .
solutionset4 <hasValue> "1" .
solutionset4 <hasValue> "3" .
equationsolving1 <hasSolution> "solutionset5" .
equations.SolutionSet(solutionset5) .
solutionset5 <hasValue> "1" .
solutionset5 <hasValue> "3" .
```

Currently the program can find real roots to quadratic equations and eigen values of 2x2 matrix.
