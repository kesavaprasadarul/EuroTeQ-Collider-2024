# EUROTEQ - CLOUDHIVE - Team 11
## Apr - May, 2024 | TUM

This repository is a stash for all the code base developed during the EuroTeQ Collider 2024 from the TUM locations.
Please follow carefully about the requirements, working and the necessary dependencies to properly run the solution.

## Solution Overview
The solution is multi-faceted: there are several levels of systems running to perform the following:
* Routing: OSRM with modified profile, adapted from several sources, thermodynamics and known restrictions in road conditions
* Elevation: OpenElevation: but with default OSM maps from SRTM
* Map Source: MapTiler maps for visual, with the default style source. Be sure to download, at minimum the Germany map tiles for better visualization.
* OSM Maps Sources: Literally the OSM source, but we had to download the whole world source
* CO2 Estimation Algorithms: Mass, Force and Emission body systems are merged on a single API for feedback. Refer to the report for theory.

## Solution Pre-requisites
* Download the whole world map, so it works better to route CH algorithms in cross-border. At minimum, we'd recommend Europe as a territory to work with, else mapping between cross-country: for example Munich to Austria won't work.
* Preprocess OSRM with CH, and not MLD. MLD is not ideal for our usecase for several reasons, the scheduling is done way ahead of the actual trip, so the dynamic mapping isn't required. CH allows you to have incredibly high speed, robust measurements and repeatable measurements which are important for validation.

## Notes
* The solution is multi-platform. Relevant requirements.txt file is provided for python relevant components, while JS components have the package file.