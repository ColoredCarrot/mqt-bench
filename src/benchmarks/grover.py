from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, AncillaRegister
from qiskit.circuit.library import GroverOperator
from qiskit.qasm import pi

def create_circuit(n: int):
    from qiskit.algorithms import Grover

    n = n - 1 #magic number due to the ancilla qubit
    q = QuantumRegister(n, 'q')
    flag = AncillaRegister(1, 'flag')
    c = ClassicalRegister(n)

    state_preparation = QuantumCircuit(q, flag)
    state_preparation.h(q)
    state_preparation.x(flag)

    oracle = QuantumCircuit(q, flag)
    oracle.mcp(pi, q, flag)

    operator = GroverOperator(oracle)
    iterations = Grover.optimal_num_iterations(1, n)

    qc = QuantumCircuit(q, flag, c, name='grover')
    qc.compose(state_preparation, inplace=True)

    qc.compose(operator.power(iterations), inplace=True)
    qc.measure_all()

    return qc

