import math
from dataclasses import dataclass

@dataclass
class Cosomology:
    H0: float
    OmegaM: float
    OmefaL: float

    @property
    def OmegaK(self):
        """Dimensionless curvature density of the Universe.
        
        $\OmegaM + \OmegaL + \OmegaK = 1$,
        $\Omega_M$ is matter density parameter and 
        $\Omega_L$ is density paramter of Dark Energy.
        

        Returns:
            OmegaK(float): Density paramter resulting from curvatur.
        """
        OmegaK = 1 - self.OmegaM - self.OmegaL
        return OmegaK

    @property
    def G(self):
        """Newtonian gravitational constant."""
        # TODO: whyyyyy?
        G = 3/2 * self.OmegaM * self.H0**2
        return G

    
    def adot(self):
        """Time derivative of dimensionless expansion factor.

        Friedmann equation: $H^2 / H_0^2 = \Omega_Lambda + \Omega_M / a^3 + \Omega_k / a^2$
        
        Returns:
            $\dot{a}$(float): Time derivate of dimensionless expansion factor.
        """
        adot = self.H0 * a * math.sqrt(self.OmegaL + (self.OmegaM / a**3) + (self.OmegaK / a**2))
        return adot

    def growing_mode(self, a):
        pass
