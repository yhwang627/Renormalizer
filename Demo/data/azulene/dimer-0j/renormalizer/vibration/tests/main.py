from renormalizer.model import Model, Op
from renormalizer.mps import Mps, Mpo, MpDm, ThermalProp
from renormalizer.utils.constant import *
from renormalizer.model import basis as ba
from renormalizer.utils import OptimizeConfig, EvolveConfig, CompressConfig, CompressCriteria, EvolveMethod
from renormalizer.vibronic import VibronicModelDynamics
from renormalizer.utils import log, Quantity
from renormalizer.vibration import Vscf
#from renormalizer.photophysics import base

import logging
import itertools 
import numpy as np

logger = logging.getLogger(__name__)

dump_dir = "./"
job_name = "test"  ####################
log.register_file_output(dump_dir+job_name+".log", mode="w")

fdusin = "/home/jjren/Research/knr/azulene/momap/std/zt_do/evc.dint.dat"
fnac = "/home/jjren/Research/knr/azulene/momap/std/zt_do/evc.cart.nac"
e_ad = 0.0750812420000102
#w0, w1, d0, d1, nac, s021, s120 = base.single_mol_model(fdusin, fnac, projector=6)
w0 = np.load("w0.npy")
w1 = np.load("w1.npy")
d0 = np.load("d0.npy")
d1 = np.load("d1.npy")
s021 = np.load("s021.npy")
s120 = np.load("s120.npy")
logger.info(f"w: {w1*au2cm}")
logger.info(f"s1 energy: {e_ad+np.sum(w1)/2}")

nmodes = len(w0)

# construct the model
ham_terms = []
# kinetic
for imode in range(nmodes):
    ham_terms.append(Op("p^2", f"v_{imode}", factor=1/2, qn=0))

# potential es coordinates
for imode in range(nmodes):
    ham_terms.append(Op("x^2", f"v_{imode}",
        factor=w0[imode]**2/2, qn=0))

#for imode, jmode in itertools.product(range(nmodes), repeat=2):
#    ham_terms.append(Op("a^\dagger a x x", ["ex", "ex", f"v_{imode}",
#        f"v_{jmode}"], factor=np.einsum("k,k,k ->", s021[imode,:], w1**2/2,
#            s021[jmode,:]), qn=[1,-1,0,0]))
#
#ham_terms.append(Op("a^\dagger a", ["ex", "ex"], factor=np.sum(w1**2/2*d1**2),
#    qn=[1,-1]))
#
#for imode in range(nmodes):
#    ham_terms.append(Op("a^\dagger a x", ["ex", "ex", f"v_{imode}"], 
#        factor=np.einsum("k,k,k ->", s021[imode,:], w1**2, d1),
#        qn=[1,-1,0]))
#
#ham_terms.append(Op("a^\dagger a", ["ex","ex"], factor=e_ad, qn=[1,-1]))

basis = []
for imode in range(nmodes):
    basis.append(ba.BasisSHO(f"v_{imode}", w0[imode], 20))
#basis.insert(nmodes//2, ba.BasisMultiElectron(["gs","ex"], [0,1]))

model = Model(basis, ham_terms)
scf = Vscf(model)
scf.kernel()
for imode in range(nmodes):
    logger.info(f"imode:{imode}, {w0[imode]*au2cm}")
    logger.info(f"{scf.e[imode]*au2cm-np.sum(w0)*au2cm/2}")
    logger.info(f"{scf.c[imode]}")