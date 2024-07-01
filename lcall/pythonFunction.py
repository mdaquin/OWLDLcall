import logging

from lcall.callableThing import CallableThing


class PythonFunction(CallableThing):
    """
    Object representing a python code to call

    It has an "expr" part corresponding to a function taking parameters of the call as direct arguments
    and can have an "exec" part with code to set up the environment
    """

    def __init__(self, expr_code: str, exec_code: str):
        """
        Initialization

        :param expr_code: expression representing a function (lambda or direct definition)
        :param exec_code: setup code executed (imports, function definitions)
        :param range: the range of the new instance to create if it is a object property (None otherwise)
        """
        self.expr_code = expr_code
        self.exec_code = exec_code

    def exec(self, params: list):
        """
        Execute the call formula calculation

        :param params: parameter values to use
        :return: result of the execution of the function
        """
        try:
            # Execute setup code if it exists
            if self.exec_code is not None:
                exec(self.exec_code)

            # Evaluate function expression
            res = eval(self.expr_code)

            # Return call result to the evaluated function
            return res(*params)
        except BaseException as e:
            logging.error("Call failed", exc_info=e)
            return None

    def __repr__(self):
        return self.expr_code+" (py)"
