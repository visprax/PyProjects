import ctypes
import pathlib
import logging

logger = logging.getLogger("interface")


class Params(ctypes.Structure):
    """Class to match C library Params struct."""
    
    _fields_ = [("num_particles", ctypes.c_size_t),
                ("gravitational_constant", ctypes.c_double),
                ("softening_length", ctypes.c_double),
                ("time_step", ctypes.c_double),
                ("com_coords", ctypes.c_int)]

    def __init__(self, params):
        self.N  = params["num_particles"]
        self.G  = params["gravitational_constant"]
        self.Rs = params["softening_length"]
        self.dt = params["time_step"]
        self.cm = params["com_coords"]

    def __repr__(self):
        rep_str  = "N (number of particles): {}\n".format(self.num_particles)
        rep_str += "G (gravitational constant): {}\n".format(self.gravitational_constant)
        rep_str += "Rs (softening length): {}\n".format(self.softening_length)
        rep_str += "dt (time step): {}\n".format(self.time_step)
        rep_str += "cm (center of mass coordinates): {}".format(self.com_coords)
        return rep_str

class Particle(ctypes.Structure):
    """Class to match C library Particle struct."""
    
    _fields_ = [("position", ctypes.c_double * 3),
               ("velocity", ctypes.c_double * 3),
               ("mass",     ctypes.c_double)]
    
    def __repr__(self):
        rep_str  = "(x, y, z) = ({}, {}, {})\n".format(\
                self.position[0], \
                self.position[1], \
                self.position[2])
        rep_str += "(vx, vy, vz) = ({}, {}, {})\n".format(\
                self.velocity[0], \
                self.velocity[1], \
                self.velocity[2])
        rep_str += "mass = {}\n".format(self.mass)
        return rep_str


class Solver:
    """Class that wraps the library functions."""
    
    _libg_path = pathlib.Path("../libg/libg.so")
    
    def __init__(self, params):
        self.params  = params
        self.libg = self.libg()


    
    def libg(self):
        libg_path = pathlib.Path("../libg/libg.so")
        if not libg_path.exists():
            logger.critical(f"shared object library not found at: {libg_path}")
            raise SystemExit()
        try:
            self.libg = ctypes.cdll.LoadLibrary(libg_path)
        except:
            logger.critical(f"couldn't load the library at: {libg_path}", exc_info=True)
            raise SystemExit()

    def init_particles(self):
        argtypes = [Params]
        restype  = [ctypes.POINTER(Particle)]
        init_particles = self.wrap_function(init_particles, )
    
    def wrap_function(self, funcname, argtypes, restype):
        """Simplify wrapping C functions."""
        func = self.libg.__getattr__(funcname)
        func.argtypes = argtypes
        func.restype  = restype
        return func



libg.compute_forces.argtypes = [ctypes.Structure]
libg.compute_forces.restype  = ctypes.double_p
