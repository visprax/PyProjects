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
<img style="position:relative;top:3.7px;" src="https://latex.codecogs.com/svg.image?\inline&space;\large&space;\boldsymbol{r}(t)&space;=&space;a(t)\boldsymbol{x}" title="https://latex.codecogs.com/svg.image?\inline \large \boldsymbol{r}(t) = a(t)\boldsymbol{x}" />
where we have chosen the dimensionless expansioin factor, 
<img src="https://latex.codecogs.com/svg.image?\inline&space;\boldsymbol{r}" title="https://latex.codecogs.com/svg.image?\inline \boldsymbol{r}" />
such that 
<img style="position:relative;top:3.7px;" src="https://latex.codecogs.com/svg.image?a(t&space;=&space;0)&space;=&space;a(t_0)&space;=&space;1" title="https://latex.codecogs.com/svg.image?a(t = 0) = a(t_0) = 1" />
for the present cosmic epoch and by definition 
<img style="position:relative;top:3.7px;" src="https://latex.codecogs.com/svg.image?\inline&space;\large&space;a(t&space;=&space;0)&space;=&space;0" title="https://latex.codecogs.com/svg.image?\inline \large a(t = 0) = 0" ></img>
at the very time of the Big Bang itself. *comoving position*
<img src="https://latex.codecogs.com/svg.image?\inline&space;\large&space;\textbf{x}" title="https://latex.codecogs.com/svg.image?\inline \large \textbf{x}" /> 
in a [Friedmann–Lemaître–Robertson–Walker](http://www.personal.psu.edu/duj13/ASTRO545/notes/ch2-FRWuniverse.pdf) (FRW) Universe (a Homogeneous and Isotropic Expanding Universe) 
remains fixed as if it's attached to the backgroud (and will change correspondingly to gravitational perturbations), <img src="https://latex.codecogs.com/svg.image?\inline&space;\boldsymbol{r}" title="https://latex.codecogs.com/svg.image?\inline \boldsymbol{r}" />
of an object will change both due to evolving <img style="position:relative;top:3.7px;" src="https://latex.codecogs.com/svg.image?\inline&space;a(t)" title="https://latex.codecogs.com/svg.image?\inline a(t)" />
and time dependent comoving coordinate <img style="position:relative;top:3.7px;" src="https://latex.codecogs.com/svg.image?\inline&space;\textbf{x}(t)" title="https://latex.codecogs.com/svg.image?\inline \textbf{x}(t)" />.

In an unperturbed Universe the density of the background has the same value throughout the Universe, <img src="https://latex.codecogs.com/svg.image?\inline&space;\rho(\boldsymbol{r},&space;t)&space;=&space;\rho_u(t)" title="https://latex.codecogs.com/svg.image?\inline \rho(\boldsymbol{r}, t) = \rho_u(t)" />.
The density perturbation at a comoving location <img src="https://latex.codecogs.com/svg.image?\inline&space;\textbf{x}" title="https://latex.codecogs.com/svg.image?\inline \textbf{x}" /> is:
<p align="center">
<img src="https://latex.codecogs.com/svg.image?\delta(\textbf{x},&space;t)&space;=&space;\frac{\rho(\textbf{x},&space;t)&space;-&space;\rho_u(t)}{\rho_u(t)}" title="https://latex.codecogs.com/svg.image?\delta(\textbf{x}, t) = \frac{\rho(\textbf{x}, t) - \rho_u(t)}{\rho_u(t)}" />
</p>

In an unperturbed FRW Universe all matter is moving along with the Hubble expansion, characterized by the Hubble parameter <img style="position: relative; top: 3.7px;" src="https://latex.codecogs.com/svg.image?\inline&space;H(t)" title="https://latex.codecogs.com/svg.image?\inline H(t)" />,
<p align="center">
<img src="https://latex.codecogs.com/svg.image?\inline&space;H(t)&space;=&space;\frac{\dot{a}}{a}" title="https://latex.codecogs.com/svg.image?\inline H(t) = \frac{\dot{a}}{a}" />
<p>

The total velocity of an object, <img src="https://latex.codecogs.com/svg.image?\inline&space;\boldsymbol{u}" title="https://latex.codecogs.com/svg.image?\inline \boldsymbol{u}" />, is:
<p align="center">
<img src="https://latex.codecogs.com/svg.image?\inline&space;\boldsymbol{u}&space;=&space;\frac{d&space;\boldsymbol{r}}{dt}&space;=&space;\dot{a}\textbf{x}\&space;&plus;&space;\&space;a\dot{\textbf{x}}&space;=&space;\textbf{v}_H(\textbf{x},&space;t)\&space;&plus;&space;\&space;\textbf{v}(\textbf{x},&space;t)&space;=&space;\\&space;\textit{\&space;\&space;\&space;\&space;\&space;\&space;\&space;\&space;\&space;\&space;\&space;\&space;\&space;\&space;\&space;&space;\text{Hubble&space;velocity&space;}}&space;&plus;&space;\text{&space;\textit{peculiar&space;velocity}}" title="https://latex.codecogs.com/svg.image?\inline \boldsymbol{u} = \frac{d \boldsymbol{r}}{dt} = \dot{a}\textbf{x}\ + \ a\dot{\textbf{x}} = \textbf{v}_H(\textbf{x}, t)\ + \ \textbf{v}(\textbf{x}, t) = \\ \textit{\ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \text{Hubble velocity }} + \text{ \textit{peculiar velocity}}" />
<p>

We denote the gravitation field of density perturbation by 






### Resources

- [Linear Perturbation Theory](https://www.astro.rug.nl/~weygaert/tim1publication/lss2009/lss2009.linperturb.pdf)
- [nbody2d](https://jhidding.github.io/nbody2d/)
- [Comological Particle Mesh Simulations](https://github.com/grkooij/Cosmological-Particle-Mesh-Simulation)
- [N-Body/Particle Simulation Methods](https://www.cs.cmu.edu/afs/cs/academic/class/15850c-s96/www/nbody.html)
