# tests called functions

def poly_degree(unk_name: str, equality: str):
    import sympy as sp
    unk = sp.symbols(unk_name)
    eq_str = equality.split("=")
    if len(eq_str) != 2:
        return None
    else:
        eq = sp.Eq(sp.sympify(eq_str[0]), sp.sympify(eq_str[1]), evaluate=False).simplify().as_poly(unk)
        if eq is None:
            return None
        else:
            deg = eq.degree(unk)
            return -1 if deg == -sp.oo else deg

def poly_obvious_roots(unk_name: str, equality: str):
    import sympy as sp
    unk = sp.symbols(unk_name)
    eq_str = equality.split("=")
    if len(eq_str) != 2:
        return None
    else:
        eq = sp.Eq(sp.sympify(eq_str[0]), sp.sympify(eq_str[1])).simplify().as_poly()
        print(eq)
        for value in range(-2, 3):
            subst_expr = eq.subs(unk, value)
            print(subst_expr)
            res = subst_expr.evalf()
            # if we found an obvious root
            if res == 0:
                root1 = value
                coeffs = eq.all_coeffs()
                root2 = -(coeffs[1]/coeffs[0])-root1
                if root2 == root1:
                    return [root1]
                else:
                    return [root1, root2]
        return None

def matrix_is_squared(expr:str):
    import sympy as sp
    mat = sp.Matrix(eval(expr))
    return mat.is_square

def get_matrix_characteristic_pol(expr:str):
    import sympy as sp
    mat = sp.Matrix(eval(expr))
    if not mat.is_square:
        return None
    else:
        return mat.charpoly("x").as_expr()

def polToEquationGetExpression(expr:str):
    return expr.replace("X", "t")+" = 0"

def polToEquationGetUnknownName(expr:str):
    return "t"

def polToEquationGetUnknownType(expr:str):
    return "real"
