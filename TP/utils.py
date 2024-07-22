import numpy as np
import random
import matplotlib.pyplot as plt
import time
import qiskit
from qiskit.circuit import *
from qiskit.circuit.library import UnitaryGate
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector, random_unitary
from qiskit import transpile
from qiskit.visualization import plot_bloch_multivector, plot_histogram
from IPython.display import display, clear_output
from qiskit.quantum_info.operators import Operator
from qiskit_ibm_runtime import QiskitRuntimeService, Session
from qiskit_ibm_runtime import SamplerV2 as Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

# Function to run a quantum circuit
def run(qc, n_shots=1024, plot=True):
    simulator = AerSimulator()
    result = simulator.run(transpile(qc, simulator),shots=n_shots).result()
    counts = result.get_counts()
    if plot:
        return plot_histogram(counts)
    else:
        return counts

# Function to plot the Bloch Sphere
def draw_state(qc,latex=False):
    new_qc = qc.copy()
    new_qc.save_statevector()
    simulator = AerSimulator()
    result = simulator.run(transpile(new_qc, simulator)).result()
    psi = result.get_statevector(new_qc)
    if latex:
        return psi.draw("latex")
    else:
        return plot_bloch_multivector(psi)
        
# Function to verify if the Draper Adder is correctly implemented, sub is set to True if we want to compute y-x instead of x+y
def draper_verification(qc,x,y,sub=False):
    n = max(len(bin(x)[2:].zfill(0)),len(bin(y)[2:].zfill(0)))
    outcome = run(qc,plot=False)
    if sub:
        res = bin((y-x)%2**n)[2:].zfill(n) == list(outcome.keys())[0]
    else:
        res = bin((y+x)%2**n)[2:].zfill(n) == list(outcome.keys())[0]
    return res
    
# Returns the list of available devices
def devices(token):
    service = QiskitRuntimeService(channel='ibm_quantum',token=key)
    QiskitRuntimeService.save_account(channel='ibm_quantum',token=key,overwrite=True)
    return  service.backends(simulator=False, operational=True)
    
# Run the circuit on the least busy quantum device if no device name is provided
def run_ibm(qc,token,device=None):
    service = QiskitRuntimeService(channel='ibm_quantum',token=key)
    QiskitRuntimeService.save_account(channel='ibm_quantum',token=key,overwrite=True)
    if device == None:
        backend = service.least_busy(operational=True, simulator=False)
    else:
        backend = service.backend(name=device)
    pm = generate_preset_pass_manager(target=backend.target, optimization_level=1)
    qc_ibm = pm.run(qc)
    with Session(service=service, backend=backend) as session:
        # Submit a request to the Sampler primitive within the session.
        sampler = Sampler(mode=session)
        job = sampler.run([qcibm])
        pub_result = job.result()[0].data.cr.get_counts()
    return pub_result
