# HexMCTS.jl

## Intro

This is a julia implementation of HexWuZi, including MCTS algorithm in julia and GameUI in python.

This julia version is much faster than `python with numba` version.

## Play it

GameUI.py is the main script of Game, just run it and enjoy the game. However, you should install all dependency first, please follow requirement section to install them well.

## Requirement

### Julia

Go to [Juila Official Website](https://julialang.org/downloads//) to download and install one.

### PyCall.jl

```julia
import Pkg
Pkg.add("PyCall")
```

### `julia` package in Python

```shell
pip install julia
```

## Performance comparation of each version

| Version           | Perfomance(times of simulation in 5 seconds) |
| ----------------- | -------------------------------------------- |
| Pure Python       | 800-900                                      |
| Python with Numba | 8k-9k                                        |
| Pure Julia        | 35k-40k                                      |