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
        roots = []
        for value in range(-2, 3):
            subst_expr = eq.subs(unk, value)
            res = subst_expr.evalf()
            if res == 0:
                roots.append(value)
                # there should be something calculated the other root but I'll do it later
        return roots

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


print(get_matrix_characteristic_pol("[[2, 1], [1, 2]]"))
print(poly_obvious_roots("x", "x**2 = 0"))
