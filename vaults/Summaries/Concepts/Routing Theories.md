The OSRM system creates a priority system for routing based on thresholds and default set for various properties in the vehicle, for example: maximum velocity, dimensions of vehicle, allowed and disallowed areas, capability to take U-Turns and such.

The default profile is tuned to cars or bikes, but is not suitable for heavy vehicles due to abnormal dimensions and engine capabilities. Cars are usually driven in priority comfort while routing, while trucks are often prioritised for safer routes.

## Thresholds and Assumptions

Following are the assumptions made for the routing engine to account in mapping:

| Attribute                                                                                        | Value            |
| ------------------------------------------------------------------------------------------------ | ---------------- |
| Maximum Driving Speed                                                                            | 150 km/h         |
| Driving Objective (Shortest Duration (selected for cars), Shortest Distance or Best Routability) | Best Routability |
| Tendency to avoid U-Turns (rated as penalty: default 20)                                         | 30               |
| Tendency to continue on straight path (rated as priority from 0-10, 10 being height: default 4)  | 8                |
| Tendency to avoid turns (rated as penalty: default 7.5)                                          | 25               |
| Left-Handed Driving                                                                              | False            |
| Cardinal Directions                                                                              | False            |
| Vehicle Average Height (default 2.5 meters)                                                      | 2.8 meters       |
| Vehicle Average Width (default 1.9 meters)                                                       | 2.2 meters       |
| Vehicle Average Length (default 4.8 meters)                                                      | 6.0 meters       |
| Vehicle Unladen Weight (default 3500 kg)                                                         | 6000 kg          |
| Tendency to re-visit roads (rated as priority from 0-10, 10 being height: default 2)             | 0                |
#### Penalties

> This is not part of default OSRM policies, and is added as a new feature in OSRM directly.

Following penalties are awards based on type of roads attributed to "highway", care should be dealt, that each lane is a road:

| Road Type                                                       | Penalty <br>(higher value results in <br>less desirability, rated 0-1) |
| --------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Motorway                                                        | 1                                                                      |
| Motorway Links                                                  | 1                                                                      |
| Trunk Roads                                                     | 1                                                                      |
| Trunk Road Links                                                | 1                                                                      |
| Primary (Full sized, <br>example Autobahn <br>full-speed lanes) | 1                                                                      |
| Primary Links                                                   | 1                                                                      |
| Secondary (middle-lanes)                                        | 1                                                                      |
| Secondary Links                                                 | 1                                                                      |
| Tertiary (slowest lanes)                                        | 0.9                                                                    |
| Tertiary Links                                                  | 0.9                                                                    |
| Unclassified Roads                                              | 0.9                                                                    |
| Residential Highways                                            | 0.7                                                                    |
| Living Streets                                                  | 0.3                                                                    |
| Service Roads                                                   | 0.2                                                                    |
| Track Roads                                                     | 0.1                                                                    |

