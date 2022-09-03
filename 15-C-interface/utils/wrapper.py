import ctypes
import pathlib
import logging
import functools

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
        rep_str  = "N (number of particles): {}\n".format(self.N)
        rep_str += "G (gravitational constant): {}\n".format(self.G)
        rep_str += "Rs (softening length): {}\n".format(self.Rs)
        rep_str += "dt (time step): {}\n".format(self.dt)
        rep_str += "cm (center of mass coordinates): {}".format(self.cm)
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
    _libg_path = "../libg/libg.so"
    
    def __init__(self, params):
        self.params = params
        self.libg = self.load_library()
        
        # self.init_particles = self._init_particles()
        # using the functools.partial we remove the need for specifying the params
        # argument every time we call a method in the library.
        self.init_particles = functools.partial(self._init_particles(), self.params)
        self.init_forces = functools.partial(self._init_forces(), self.params)
        self.kinetic_energy = self._kinetic_energy()
        self.potential_energy = self._potential_energy()
        self.momentum = self._momentum()
        self.compute_forces = self._compute_forces()
        self.direct_nbody =  self._direct_nbody()
    
    @classmethod
    def load_library(cls, path=None):
        """Load the C shared library.

        Note that the implementation of this method using the 
        classmethod decorator is done for an example use case 
        of the decorator, we could have simply implemented it
        without using a classmethod, e.g. using a staticmethod,
        an instance method, or simply in the __init__ method.

        Args:
            path (str): The path to shared object library.

        Returns:
            libg (ctypes.CDLL): ctypes.CDLL handle to shared object library.
        """
        if not path:
            path = cls._libg_path
        path = pathlib.Path(path)
        if not path.exists():
            logger.critical(f"shared object library not found at: {path}")
            raise SystemExit()

        try:
            libg = ctypes.cdll.LoadLibrary(path)
        except:
            logger.error(f"couldn't load the library at: {path}", exc_info=True)
            libg = None
        finally:
            return libg

    def func_wrapper(self, funcname, argtypes, restype):
        """Helper method to wrap C functions."""
        func = self.libg.__getattr__(funcname)
        func.argtypes = argtypes
        func.restype  = restype
        return func

    def _init_particles(self):
        argtypes = [Params]
        restype  = ctypes.POINTER(Particle)
        return self.func_wrapper("init_particles", argtypes, restype)

    def _init_forces(self):
        argtypes = [Params]
        restype  = ctypes.POINTER(c_double)
        return self.func_wrapper("init_forces", argtypes, restype)

    def _kinetic_energy(self):
        argtypes = [ctypes.POINTER(Particle), Params]
        restype  = ctypes.c_double
        return self.func_wrapper("kinetic_energy", argtypes, restype)

    def _potential_energy(self):
        argtypes = [ctypes.POINTER(Particle), Params]
        restype  = ctypes.c_double
        return self.func_wrapper("potential_energy", argtypes, restype)

    def _momentum(self):
        argtypes = [ctypes.POINTER(Particle), Params]
        restype  = ctypes.c_double
        return self.func_wrapper("momentum", argtypes, restype)

    def _compute_forces(self):
        argtypes = [ctypes.POINTER(Particle), ctypes.POINTER(c_double), Params]
        restype  = None
        return self.func_wrapper("compute_forces", argtypes, restype)

    def _direct_nbody(self):
        argtypes = None
        restype  = None
        return self.func_wrapper("direct_nbody", argtypes, restype)

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s  %(name)s  %(levelname)s: %(message)s')
    logger.setLevel(logging.DEBUG)

    params_dict = {
            "num_particles": 100,
            "gravitational_constant": 1.0,
            "softening_length": 0.05,
            "time_step": 1e-4,
            "com_coords": 0
            }
    params = Params(params_dict)

    solver = Solver(params)

    # particles = solver.init_particles(params)
    particles = solver.init_particles()
    print(particles[0])
