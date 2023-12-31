# HexMCTS.jl

## Intro

This is a julia implementation of HexWuZi, including MCTS algorithm in julia and GameClient in python.

This julia version is much faster than `python with numba` version, see `Performance comparison of each version` section for more detail.

## `What's new!`

Since the old version can't run well on my new macbook, I write a new julia program to host a web server to communicate between julia backend and python fontend instead. This new version can run well both on macos and windows.

## Play it

1. Start the `BackendServer` with running the `BackendServer.jl`
    ```shell
    julia BackendServer.jl
    ```

2. Start the `GameClient` with running the `GameClient.py`
    ```shell
    python GameClient.py
    ```

However, you should install all dependency first, please follow `Requirement` section to install them well.

## Requirement

### Julia

Go to [Juila Official Website](https://julialang.org/downloads//) to download and install one.

### Oxygen

We use [`Oxygen`](https://github.com/ndortega/Oxygen.jl) package for web development in julia, you have to install it first.

```julia
import Pkg
Pkg.add("Oxygen")
```

> Since the old version with `julia` package in python and `PyCall.jl` in julia can't run well on my new macbook, I write a new julia program to host a web server to communicate between julia backend and python fontend instead.

## Performance comparison of each version

| Version           | Perfomance(times of simulation in 5 seconds) |
| ----------------- | -------------------------------------------- |
| "Pure Python"     | 800-900                                      |
| Python with Numba | 8k-9k                                        |
| Pure Julia        | 35k-40k                                      |

> Why there is quotation mark around "Pure Python"?
> 
> Because if you use NumPy, then it's not pure any more since NumPy is written in C.
