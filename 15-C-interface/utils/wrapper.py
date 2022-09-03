import ctypes
import pathlib
import logging

# logger = logging.getLogger("interface")

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
    
    _libg_path = "../libg/libg.so"
    
    def __init__(self, params):
        # TODO: checks for params
        self.params  = params
        self.libg = self.load_library()
    
    @classmethod
    def load_library(cls, path=None):
        """Load the C shared library.

        Note that the implementation of this method using the 
        classmethod decorator is done for an example use case 
        of the decorator, we could have simply implemented it
        without using a classmethod, e.g. using a staticmethod
        or simply an instance method.

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

    def wrap_function(self, funcname, argtypes, restype):
        """Simplify wrapping C functions."""
        func = self.libg.__getattr__(funcname)
        func.argtypes = argtypes
        func.restype  = restype
        return func

    def init_particles(self):
        argtypes = [Params]
        restype  = [ctypes.POINTER(Particle)]
        init_particles = self.wrap_function(init_particles, )


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s  %(name)s  %(levelname)s: %(message)s')
    logger = logging.getLogger("wrapper")
    logger.setLevel(logging.DEBUG)
    
    solver = Solver(1)
    solver.load_library("sdcdc.so")
    # solver.libg = Solver.load_library("../libg/libg.so")
    # solver.libg = Solver.load_library()
    print(solver.libg)
