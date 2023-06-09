import numpy as np
import itertools

from renormalizer.model import Op, Model
from renormalizer.utils import constant, Quantity
from renormalizer.model import basis as ba


elocalex = Quantity(2.67, "eV").as_au()
dipole_abs = 15.45
nmols = 3

# eV
_j_matrix = (
    np.array([[0.0, -0.1, -0.2], [-0.1, 0.0, -0.3], [-0.2, -0.3, 0.0]]) / constant.au2ev
)

omega = [Quantity(106.51, "cm^{-1}").as_au(), Quantity(1555.55, "cm^{-1}").as_au()]
displacement = [Quantity(30.1370, "a.u.").as_au(), Quantity(8.7729, "a.u.").as_au()]
ph_phys_dim = [4, 4]

e_reorganization = 0
for iph in range(2):
    e_reorganization += omega[iph]**2 * displacement[iph]**2 * 0.5

basis = []
for imol in range(3):
    for iph in range(2):
        basis.append(ba.BasisSHO(f"v_{imol},{iph}", omega[iph], ph_phys_dim[iph]))
basis.insert(2, ba.BasisMultiElectron(["gs","e_0","e_1","e_2"], [0,1,1,1]))

ham_terms = []
# excitonic coupling
for imol, jmol in itertools.permutations(range(nmols),2):
    ham_terms.append(Op("a^\dagger a", [f"e_{imol}", f"e_{jmol}"],
        factor=_j_matrix[imol,jmol], qn=[1,-1]))

# local excitation
for imol in range(nmols):
    ham_terms.append(Op("a^\dagger a", [f"e_{imol}", f"e_{imol}"],
        factor=elocalex+e_reorganization, qn=[1,-1]))

# harmonic part
for imol in range(3):
    for iph in range(2):
        ham_terms.append(Op("p^2", f"v_{imol},{iph}",
            factor=0.5, qn=0))
        ham_terms.append(Op("x^2", f"v_{imol},{iph}",
            factor=0.5*omega[iph]**2, qn=0))

        # e-ph coupling
        ham_terms.append(Op("a^\dagger a x", [f"e_{imol}", f"e_{imol}",f"v_{imol},{iph}"],
            factor=-omega[iph]**2*displacement[iph], qn=[1,-1,0]))

para = {"dipole":{}}
for imol in range(3):
    para["dipole"][(f"e_{imol}","gs")] = dipole_abs

model = Model(basis, ham_terms, para=para)