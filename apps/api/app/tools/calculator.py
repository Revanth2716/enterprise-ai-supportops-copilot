import ast
import operator
from typing import Union, Dict, Any

ALLOWED_BINARY_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

ALLOWED_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

MAX_EXPRESSION_LENGTH = 100
MAX_EXPONENT = 10
MAX_BASE_FOR_POW = 1_000_000
MAX_RESULT_MAGNITUDE = 1_000_000_000_000  # 10^12


class RestrictedASTEvaluator:
    """
    Restricted AST Evaluator for safe arithmetic calculation.
    Permits ONLY:
    - Numeric constants (int, float)
    - +, -, *, /, %, **
    - Unary + and -
    
    Rejects:
    - Names, Attributes, Function calls, Imports, Subscripts, and arbitrary AST nodes.
    - Expressions > 100 chars
    - Disproportionate exponents (DoS prevention)
    """

    def evaluate(self, expr: str) -> float:
        if not expr or not isinstance(expr, str):
            raise ValueError("Expression must be a non-empty string.")

        expr = expr.strip()
        # Clean currency symbols
        expr = expr.replace("$", "").replace("€", "").replace("£", "")

        if len(expr) > MAX_EXPRESSION_LENGTH:
            raise ValueError(f"Expression exceeds maximum length of {MAX_EXPRESSION_LENGTH} characters.")

        try:
            tree = ast.parse(expr, mode='eval')
        except SyntaxError as se:
            raise ValueError(f"Malformed arithmetic expression: {se.msg}")

        result = self._eval_node(tree.body)

        if abs(result) > MAX_RESULT_MAGNITUDE:
            raise ValueError(f"Result exceeds safe numeric bounds ({MAX_RESULT_MAGNITUDE}).")

        return float(result)

    def _eval_node(self, node: ast.AST) -> Union[int, float]:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                return node.value
            raise ValueError(f"Unsupported constant type: {type(node.value).__name__}")

        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in ALLOWED_UNARY_OPS:
                raise ValueError(f"Unary operator {op_type.__name__} is not allowed.")
            operand = self._eval_node(node.operand)
            return ALLOWED_UNARY_OPS[op_type](operand)

        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in ALLOWED_BINARY_OPS:
                raise ValueError(f"Binary operator {op_type.__name__} is not allowed.")

            left_val = self._eval_node(node.left)
            right_val = self._eval_node(node.right)

            # Division by zero guard
            if op_type in (ast.Div, ast.Mod) and right_val == 0:
                raise ValueError("Division or modulo by zero is undefined.")

            # Power DoS protection
            if op_type is ast.Pow:
                if not isinstance(right_val, (int, float)) or right_val > MAX_EXPONENT or right_val < -MAX_EXPONENT:
                    raise ValueError(f"Exponent must be between -{MAX_EXPONENT} and {MAX_EXPONENT}.")
                if abs(left_val) > MAX_BASE_FOR_POW:
                    raise ValueError("Base is too large for power operation.")

            res = ALLOWED_BINARY_OPS[op_type](left_val, right_val)
            return res

        elif isinstance(node, (ast.Name, ast.Attribute, ast.Call, ast.Import, ast.ImportFrom, ast.Subscript)):
            raise ValueError(f"Disallowed security-sensitive syntax detected: {type(node).__name__}")

        else:
            raise ValueError(f"Disallowed AST node type: {type(node).__name__}")


def safe_calculate(expression: str) -> Dict[str, Any]:
    evaluator = RestrictedASTEvaluator()
    try:
        ans = evaluator.evaluate(expression)
        return {
            "success": True,
            "expression": expression,
            "result": ans,
            "formatted": f"{ans:.2f}"
        }
    except Exception as e:
        return {
            "success": False,
            "expression": expression,
            "error": str(e)
        }
