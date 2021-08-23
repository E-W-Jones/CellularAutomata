# Cellular Automata

A cellular automaton is, at its simplest, a grid that is updated by considering one cell and its immediate neighbours at a time. Each cell has at least two states, and I will refer to them as *off* and *on*, or *0* and *1*.

## Quick Start

For more information, refer to the sections on the automata and running the programs below.

### Running one_dimensional.py
At the terminal/command line, run the following:

```shell
python one_dimension.py <number of iterations> <rule number to follow>
```

The number of iterations is the number of times that the row is updated. The rule number is explained below, but is optional. If omitted, the program runs with rule 90.

### Running gameoflife.py
Two options exist, import the `Grid` class and use that, which is more flexible, or run from the terminal.
To run from the terminal, use a file that contains a grid of 0s and 1s, (some are provided) and provide it as an argument at the terminal:
```shell
python gameoflife.py <file name>
```
The file name is optional, and if not provided a grid is used where each cell is assigned its value randomly (with 50/50 probability).

If importing the `Grid` class, it can quickly be used by creating an instance, then using the `run` function:
```python
from gameoflife import Grid as Grid

# --- Create a grid instance ---
# Using a file
grid = Grid(fname=<file name>)

# Using a random grid
grid = Grid(random=True)

# Using built in functions
grid = Grid()
grid.add_glider()  # or grid.r_pentomino()

# --- Run the Program ---
# Either for a certain number of iterations
grid.run(niter=<number of iterations>)

# Or indefinitely
grid.run()
```

## One Dimensional Cellular Automaton
A [one-dimensional cellular automaton](https://mathworld.wolfram.com/ElementaryCellularAutomaton.html) is a row of cells that update based off a set of rules, for example:

| Current State  | 111  | 110  | 101  | 100  | 011  | 010  | 001  | 000  |
| :------------: | :--: | :--: | :--: | :--: | :--: | :--: | :--: | :--: |
| Next Iteration |  0   |  1   |  0   |  1   |  1   |  0   |  1   |  0   |

Where the current state has the cell being updated in the middle, and either side is the state of the neighbouring cells. When we have a consistent order of the current state we can refer to how the cells are updated with “01011010”, which is the binary representation of the number 90. This provides a useful way to refer to each potential rule there could be. Some more potential rules are shown below.

| Current State | 111  | 110  | 101  | 100  | 011  | 010  | 001  | 000  |
| :-----------: | :--: | :--: | :--: | :--: | :--: | :--: | :--: | :--: |
|    Rule 1     |  0   |  0   |  0   |  0   |  0   |  0   |  0   |  1   |
|    Rule 30    |  0   |  0   |  0   |  1   |  1   |  1   |  1   |  0   |
|    Rule 90    |  0   |  1   |  0   |  1   |  1   |  0   |  1   |  0   |

### How to Run

At the command line, run:

```shell
python one_dimension.py <number of iterations> <rule number to follow>
```

If `<number of iterations>` is omitted, then the program will prompt the user to enter a value before continuing. If `<rule number to follow>` is omitted, then Rule 90 is used.

## Conway’s Game of Life

Conway's Game of Life uses a 2D grid of 0s and 1s, where each cell updates based off simple rules and the surrounding cells.

### Neighbourhoods

The neighbourhood is the collection of cells that are used to calculate how a cell is updated. The two most common types are **von Neumann** and **Moore** neighbourhoods. The von Neumann neighbourhood consists only of the four cells immediately above and to the sides of the cell being updated. The Moore neighbourhood consists of all 8 cells surrounding the cell being updated; the cells immediately above, below, and diagonally touching.

*Cell* is the cell being updated, and **X** marks the cells included in the neighbourhood:

#### von Neumann


|       | **X** |       |
| :---: | :---: | :---: |
| **X** | Cell  | **X** |
|       | **X** |       |

#### Moore
|   **X**    | **X** |   **X**    |
| :---: | :---: | :---: |
| **X** | Cell  | **X** |
|    **X**   | **X** |   **X**    |

### Rules

Rules for updating are often written B*abc*/S*xyz*. B stands for Born, and S for Survive. If a dead cell has *a*, *b*, or *c* live cells surrounding it then it it turns into a live cell (is born). If a live cell has *x*, *y*, or *z* live cells surrounding it continues to be a live cell (survives). All other cells either die, or stay dead.

Consider the default for the Game of Life: B2/S23. This means that if a dead cell has 2 live neighbours, it becomes live. If a live cell has 2 or 3 neighbours then it continues to be live. All other cells die, or stay dead.
