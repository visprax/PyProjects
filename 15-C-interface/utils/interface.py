import ctypes
import pathlib
import logging

logger = logging.getLogger("interface")

libg_path = pathlib.Path("../libg/libg.so")

if not libg_path.exists():
    logger.critical(f"shared object library not found at: {libg_path}")
    raise SystemExit()

try:
    libg = ctypes.cdll.LoadLibrary(libg_path)
except:
    logger.critical(f"couldn't load the library at: {libg_path}", exc_info=True)
    raise SystemExit()

class Params(ctypes.Structure):
    _fields_ = [("num_particles", ctypes.c_size_t),
                ("gravitational_constant", ctypes.c_double),
                ("softening_length", ctypes.c_double),
                ("time_step", ctypes.c_double),
                ("com_coords", ctypes.c_int)]

    __init__(self, params):
        self.N = params["num_particles"]
        self.G = params["gravitational_constant"]
        self.Rs = params["softening_length"]
        self.dt = params["time_step"]
        self.cm = params["com_coords"]

class Particle(ctypes.Structure):
    _fields = [("position", ctypes.c_double * 3),
               ("velocity", ctypes.c_double * 3),
               ("mass",     ctypes.c_double)]

    __init__(self, position, velocity, mass):
        pass

    def somethinf(self):
        return libg.compute_forces()

libg.compute_forces.argtypes = [ctypes.Structure]
libg.compute_forces.restype  = ctypes.double_p
