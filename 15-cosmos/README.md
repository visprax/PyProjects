# Cosmos

Here we will try to do particle mesh simulation of the large scale structure of the universe (only dark matter with no baryonic physics).

##### Goals:
- Interface C with Python (do heavy compuations in C)

## Physics

In an expanding Universe, its evolution is governed by the [Hubble expansion](https://en.wikipedia.org/wiki/Hubble%27s_law). 
If we take 
<img style="position:relative;top:3.7px;" src="https://latex.codecogs.com/svg.image?\inline&space;\large&space;a(t)" title="https://latex.codecogs.com/svg.image?\inline \large a(t)" />
the universal expansion factor (Hubble expansion is uniform throughout the Universe), the location of an object in physical coordinates, 
<img src="https://latex.codecogs.com/svg.image?\inline&space;\boldsymbol{r}" title="https://latex.codecogs.com/svg.image?\inline \boldsymbol{r}" />
can be written as:
<p align="center">
<img src="https://latex.codecogs.com/svg.image?\inline&space;\large&space;\boldsymbol{r}(t)&space;=&space;a(t)\boldsymbol{x}" title="https://latex.codecogs.com/svg.image?\inline \large \boldsymbol{r}(t) = a(t)\boldsymbol{x}" />
</p>
where we have chosen the dimensionless expansioin factor, 
<img style="position: relative; top: 3.7px;" src="https://latex.codecogs.com/svg.image?\inline&space;\large&space;a(t)" title="https://latex.codecogs.com/svg.image?\inline \large a(t)" />
such that <img style="position: relative; top: 3.7px;" src="https://latex.codecogs.com/svg.image?\inline&space;a(t_0)&space;=&space;a_0&space;=&space;1" title="https://latex.codecogs.com/svg.image?\inline a(t_0) = a_0 = 1" />
for the present cosmic epoch and by definition 
<img src="https://latex.codecogs.com/svg.image?\inline&space;\large&space;a(t&space;=&space;0)&space;=&space;0" title="https://latex.codecogs.com/svg.image?\inline \large a(t = 0) = 0" ></img>
at the very time of the Big Bang itself. **comoving position** 
<img src="https://latex.codecogs.com/svg.image?\inline&space;\large&space;\textbf{x}" title="https://latex.codecogs.com/svg.image?\inline \large \textbf{x}" /> 


Persumably Dark Matter doesn't interact with photon (hence dark) and electromagnetism plays no role in it's dynamics, so on the large scale gravitation 
is the sole dyanmical force, which will assume is non-relativistic for simplicity (wouldn't apply for early universe beacuse of dominat relativistic radiation).

Poisson equation governing the Newtonian gravity field:

<p align="center">
<img src="https://latex.codecogs.com/svg.image?\nabla^2\Phi&space;=&space;4\pi&space;G\rho" title="https://latex.codecogs.com/svg.image?\nabla^2\Phi = 4\pi G\rho" />
</p>

where ![Latex \rho](https://latex.codecogs.com/svg.image?%5Cinline%20%5Crho) is the matter density and ![Latex \Phi](https://latex.codecogs.com/svg.image?%5Cinline%20%5CPhi) 
is the gravitational potential.

By defining 



### Resources

- [Linear Perturbation Theory](https://www.astro.rug.nl/~weygaert/tim1publication/lss2009/lss2009.linperturb.pdf)
- [nbody2d](https://jhidding.github.io/nbody2d/)
- [Comological Particle Mesh Simulations](https://github.com/grkooij/Cosmological-Particle-Mesh-Simulation)
- [N-Body/Particle Simulation Methods](https://www.cs.cmu.edu/afs/cs/academic/class/15850c-s96/www/nbody.html)
