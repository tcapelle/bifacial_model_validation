[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/tcapelle/bifacial_model_validation_/master)


# Bifacial Model validation

This repository is to exchange modelling techniques for bifacial model validation.

## Installation

- You will need a Python 3, get it from: [Anaconda Python](https://www.anaconda.com/what-is-anaconda/)
- [Python PVLIB](https://pvlib-python.readthedocs.io/en/latest/installation.html)
- [PVFactors](https://sunpower.github.io/pvfactors/installation/index.html)
- [bifacialvf - my version](https://github.com/tcapelle/bifacialvf)

In short, if you have anaconda, execute:
```
$ conda env create --file=environment.yml
$ conda activate bifacial_model_validation
$ jupyter lab
```

## Run the notebooks:

Open Jupyter Lab (or notebook) and run them interactively.
You can also click the [binder](https://mybinder.org/v2/gh/tcapelle/bifacial_modelling/master) icon and run them on the web.

## Notebook 01

In this notebook we construct a simulation of 2D Viewfactor models. Here a `pvfactors` and `bifacialvf` simulation is done with the same inputs, using some wrapper methods around both libraries.
The idea behind is to be able to compare apples to apples both frameworks.