## Delta Altitude Reward Models

### Force Model

#### Theory

Given a vehicle moving in a flat surface, there are majorly two forces acting, with other elementary forces:
$$
F_T = (F_H + F_V) \cdot J \tag{1}
$$
$$ \begin{gathered} 
	F_T = \text{Total force exerted} \\
	F_H = \text{Horizontal Forces; dependent on load momentum} \\
	F_V = \text{Vertical Forces; load and gravity only}
\end{gathered} $$
$$F_H = m \cdot \frac{d^2V}{dT^2} \tag{2}$$
$$F_V = \frac{G\cdot M \cdot m}{r^2} \tag{3}$$
$$ J - \text{Calibratable factor calculation, typically 1} \tag{4}$$

Forces exerted due to $F_H$ are typically overpowered by the truck's engines, which essentially creates the movement and control of the freight in entirety. $F_V$ is balanced by the structural integrity of the engine.

The demand of the engine is (usually defined in terms of torque requirement), defined as $T_{dem}$. In a normalised measurement scenario, the value of $T_{dem}$ is 1 on flat roads.

However during ascent, the load $m$ is shifted from $F_V$ to $F_H$ partly, effectively increasing net $F_H$. This increases $T_{dem} \geq 1$ finally. The converse is valid; during descent, the $F_H$ is reduced since $F_H$ is moved to $F_V$.

From a single body propulsion point of view, torque demand is directly proportional to the force exerted by the vehicle to counteract $(1)$:
$$T_{dem} \propto F_T \tag{5}$$
This can be converted to a linear form: 
$$F_T = k\cdot T_{dem} \tag{6}$$
These two different simple models complement each other from different directions.

#### Effects

From vehicle combustion point of view, torque demand is directly proportional to the fuel consumed per kilometre:
$$ T_{dem} \propto Q_{km} \tag{7}$$
And similarly creating a linear form:
$$Q_{km} = k \cdot T_{dem} \tag{8}$$
With known quantities of average fuel consumption of vehicle based on class $Q_{km,avg}$, torque class $T_{eng}$ to derive $T_{dem}$ based on average mass in vehicle; it is possible to solve $(6)$ to get $k$.

Total consumed $Q_{km}$ can be calculated from $(8)$ with known $k$ and $T_{dem}$. 

On average, CO2 production from diesel is defined as:
$$CO_{2,avg} = 3.17 \text{g per g of diesel}\tag{9}$$
This is the maximum theoretical value derived from combustion of pure diesel, vehicles produce way less that aforementioned value, attributed by the after-treatment parts and active emission control devices, for example EGRs.

This lesser production can be a factor defined similar to $k$, since all equations $(6), (7) \text{ and } (9)$ are linear proportional values.
#### Known Approximations

1. Very simple force body model is used throughout the analysis: that is, a vehicle is considered a uni-body. Interacting forces are not considered, for example: momentum imbalance between load and drive-train areas of a truck, sway and other road impacts.
2. The emission systems are dependent to vary between high and low load scenarios, for example: cold-start conditions, any effects due to AECD, full-load operation and limp-mode situations.
3. The factor $k$ is considered uniform, and approximated heavily. However this can be tuned using factor $j$ that is controlled by the user, creating a closed loop system that does not affect the calculation chain in the middle, causing and unintended effects.
4. Many external forces are neglected: wind drag, aerodynamics of the vehicle, traffic situations, road smoothness.

### Combustion Model
#### Theory

Diesel Engines and all combustion engines depend on considerable amount of O2 for the proper function and torque delivery. Diesel engines rely on a stoichiometric AFR (Air-to-fuel ratio) of $14.5:1$. Essentially this would mean that to combust 1g of diesel, the engines require a minimum of 14.5g of air (in composition, all gases including H2 and N2 along with O2). This theory uses the mass-flow model to determine rate of change of consumption of air, resulting in proportional change of fuel consumption based on altitude and temperature.

Rewriting the above text mathematically,
$$MF_{air} \propto Q_{act} \tag{10}$$
$$Q_{act} = k \cdot MF_{air} \text{, where k}=14.5. \tag{11}$$
From $(9)$, we know that $\text{1g of } Q_{act} = 3.17 \text{g of CO2}$,
$$ \implies \frac{dm_{CO_2}}{dQ_{act}} = 3.17 g/g \tag{12} $$

Estimated mass flow can be calculated empirically from ideal gas equation:

$$MF_{in} = \frac{P_{env} \cdot V_{engine}}{R \cdot T_{env}} \tag{13}$$
Lapse rate due to altitude change also has a relation:
$$L = -\frac{dT}{dH} \text{ degC/m}$$
This lapse rate is known for every geographic region and is uniform over continents. This can be used to determine $dT$:
$$dT = -L \cdot dH \tag{14}$$
Considering adiabatic compression scenario, $(13)$ can also be written as:
$$P\cdot dV = - \frac{R\cdot dP}{\gamma};\ \ \ \gamma = c_p / c_v \tag{15} $$
Combine all equations and simplify from $(13)$ to $(15)$ to get:
$$MF_{air} = \frac{M\cdot C_p \cdot dV_{engine}}{R} \tag{16}$$

All values are known, except for $C_p$. This can be evaluated using Sutherland's law for mass flow and compression:
$$C_p = \frac{A+B\cdot \left( \frac{\frac{C}{T_{env}}}{sinh\left(\frac{C}{T_{env}}\right)} \right)^2 + D\cdot \left(\frac{\frac{E}{T_{env}}}{cosh\left(\frac{E}{T_{env}}\right)}\right)^2}{MW} \tag{17}$$

$$\begin{gathered}
\text{A = 28958} \\
\text{B = 9390} \\
\text{C = 3012} \\
\text{D = 7580} \\
\text{E = 1484} \\
\text{MW = 28.951 kg/mol}
\end{gathered}$$

This estimated mass flow from $(16)$ can be applied to calculate required fuel change for combustion in $(11)$, then re-applied to $(12)$ to determine change of CO2 emissions.

### Known Approximations

1. The following environmental and vehicle conditions are assumed:
	1. Ideal Gas Conditions:
		1. Temperature = 21 degC
		2. Pressure = 1014 hPa
		3. Volume = 1 litre of O2
2. The vehicle is assumed to have one turbo-charger, and is assumed primarily in adiabatic conditions in full load.
### References

1. Specific Heat Capacities: https://www.grc.nasa.gov/www/k-12/BGP/specheat.html
2. Flow Control: https://www.grc.nasa.gov/www/BGH/isndrv.html
3. Sutherland Law and corresponding values: https://ubitutors.com/thermal-properties-of-air-at-a-given-temperature/
4. Sutherland Law in terms of Conductivity: https://doc.comsol.com/5.5/doc/com.comsol.help.cfd/cfd_ug_fluidflow_high_mach.08.27.html