import ast
import operator
import logging
import re
from typing import Tuple, Union

from voice.text_to_speech import speak

logger = logging.getLogger("JARVIS.Calculator")

# Safe AST operators mapping
ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def _eval_ast_node(node):
    """Recursively evaluate safe AST node."""
    if isinstance(node, ast.Constant):  # Numbers
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Invalid constant type")
    
    elif isinstance(node, ast.BinOp):  # Binary operations (+, -, *, /)
        left = _eval_ast_node(node.left)
        right = _eval_ast_node(node.right)
        op_type = type(node.op)
        if op_type in ALLOWED_OPERATORS:
            if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right == 0:
                raise ZeroDivisionError("Division by zero")
            return ALLOWED_OPERATORS[op_type](left, right)
        raise ValueError(f"Unsupported binary operator: {op_type}")

    elif isinstance(node, ast.UnaryOp):  # Unary operations (+x, -x)
        operand = _eval_ast_node(node.operand)
        op_type = type(node.op)
        if op_type in ALLOWED_OPERATORS:
            return ALLOWED_OPERATORS[op_type](operand)
        raise ValueError(f"Unsupported unary operator: {op_type}")

    raise ValueError(f"Unsupported AST node: {type(node)}")

def safe_evaluate(expression: str) -> Union[int, float]:
    """Parse and safely evaluate mathematical expression string using AST."""
    if not expression:
        raise ValueError("Empty math expression")

    # Clean text math words into math symbols
    expr_clean = expression.lower()
    replacements = [
        ("plus", "+"),
        ("minus", "-"),
        ("multiplied by", "*"),
        ("times", "*"),
        ("x", "*"),
        ("divided by", "/"),
        ("over", "/"),
        ("power", "**"),
    ]
    for word, symbol in replacements:
        expr_clean = expr_clean.replace(word, symbol)

    # Filter allowed characters only (0-9, +, -, *, /, %, ., (), spaces)
    expr_clean = re.sub(r"[^\d\+\-\*\/\%\.\(\)\s]", "", expr_clean).strip()
    if not expr_clean:
        raise ValueError("No valid math expression found")

    # Parse into AST tree
    tree = ast.parse(expr_clean, mode='eval')
    return _eval_ast_node(tree.body)

def calculate(expression_text: str, speaker_role: str = "Boss") -> Tuple[bool, str]:
    """
    Spoken wrapper for safe calculator evaluation.
    """
    logger.info(f"Received calculation query: '{expression_text}'")
    try:
        result = safe_evaluate(expression_text)
        
        # Format integer vs float
        if isinstance(result, float) and result.is_integer():
            result = int(result)
            
        msg = f"The result is {result}."
        speak(msg)
        return True, msg

    except ZeroDivisionError:
        msg = f"Sorry {speaker_role}, division by zero is mathematically undefined."
        speak(msg)
        return False, msg

    except Exception as e:
        logger.error(f"Calculation error for '{expression_text}': {e}")
        msg = f"Sorry {speaker_role}, I couldn't compute that mathematical calculation."
        speak(msg)
        return False, msg
