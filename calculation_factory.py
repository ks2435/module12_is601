from schemas import OperationType


def calculate(a: float, b: float, operation: OperationType) -> float:
    if operation == OperationType.add:
        return a + b
    elif operation == OperationType.subtract:
        return a - b
    elif operation == OperationType.multiply:
        return a * b
    elif operation == OperationType.divide:
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    else:
        raise ValueError(f"Unknown operation type: {operation}")