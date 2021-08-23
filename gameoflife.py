# -*- coding: utf-8 -*-
"""
Author: Evan Jones
Updated: 2021/07/05

Conway's Game of life

There are 3 rules to Conway's game of life:
    1) Any live cell with two or three live neighbours survives.
    2) Any dead cell with three live neighbours becomes a live cell.
    3) All other cells die or stay dead.

This can be succintly put using a piece of common notation in cellular automata:
B3/S23

I will be using periodic boundary condtions.

* centered means as close to centre of grid as possible.
"""
import numpy as np
import os
import sys
import time
from shutil import get_terminal_size


class Grid():
    """
    A grid based on a numpy array, where the game of life is carried out.

    A 1 represents a live cell, 0 a dead one. The grid is updated according to
    three rules:
        1) Any live cell with two or three live neighbours survives.
        2) Any dead cell with three live neighbours becomes a live cell.
        3) All other cells die or stay dead.

    The result is printed to the terminal to make an animation of the game.
    """

    def __init__(self, width=None, height=None, fname=None, random=False):
        """
        Initialise a grid object, where the game of life is carried out.

        Parameters
        ----------
        width, height : int, optional
            Width and height of the grid in characters. The default is None,
            which corrosponds to using the terminal width and height.
        fname : string, optional
            File name to load the starting grid from. The default is None,
            meaning no file is used. The grid is initialised as all 0s, or
            randomly if random = True. If a file-name is given, this takes
            priority over random.
        random : boolean, optional
            If True and no file-name given, randomly assign cells on the grid
            to be dead or alive. If false and no file-name given, then the
            grid is all dead. If a file-name is given the grid is initialised
            from the file and the value of random is ignored.
            The default is False.

        Returns
        -------
        None.

        """
        self.set_clear_terminal(True)
        self.set_fps(60)
        self.set_rules(born=[3], survive=[2, 3])  # Conway's rules, B3/S23.
        self.set_neighbourhood_type("Moore")  # Consider all surrounding cells.

        # Check that the neighbourhood type and rules are compatible:
        moore = (self.neighbourhood_type == "moore")
        over_eight = (max(self.born) > 8 or max(self.survive) > 8)
        vonneumann = (self.neighbourhood_type == "vonneumann")
        over_four = (max(self.born) > 4 or max(self.survive) > 4)

        if (moore and over_eight) or (vonneumann and over_four):
            error_str = (f"Your neighbourhood type ({self.neighbourhood_type}) "
                        f"and rules ({self.get_rules()}) are incompatible.")
            raise ValueError(error_str)

        cols, rows = get_terminal_size()
        cols -= 1
        rows -= 1

        if width is None:
            width = cols if (cols % 2 == 0) else cols - 1  # Round down to even
        if height is None:
            height = rows if (rows % 2 != 0) else rows - 1  # Round down to odd
        if width < 5 or height < 5:
            sys.exit("Please choose a bigger grid, at least 5x5.")

        # Take two off of each, to account for the border
        self.width = width - 2
        self.height = height - 2

        self.grid = np.zeros((self.height, self.width))

        if fname is not None:
            self.read_from_file(fname)
        elif random:
            rng = np.random.default_rng()
            self.grid = rng.integers(low=0, high=2,  # from the range [0, 2)
                                     size=(self.height, self.width))

    def set_clear_terminal(self, value):
        """
        Set if the terminal's cleared before the new grid is printed.

        Parameters
        ----------
        value : boolean
            True means the terminal is cleared of the old grid before the new
            grid is printed. False means it is not.

        Returns
        -------
        None.

        """
        if isinstance(value, bool):
            self.clear = value
        else:
            raise TypeError(("When calling set_clear_terminal, value should "
                            f"be boolean, not {str(type(value))[8:-2]}"))

    def set_fps(self, value):
        """
        Set the frames per second of the resulting animation.

        Parameters
        ----------
        value : float or int
            The number of frames per second. Alternatively, the inverse of the
            time between frames being printed.

        Returns
        -------
        None.

        """
        self.fps = value

    def set_rules(self, born, survive):
        """
        Set the rules that decide how the cells update.

        Designed to follow the Babc/Sxyz notation used in cellular automata.
        Babc means that if there are a or b or c alive cells around a dead cell,
        it becomes a live cell at the start of the next turn, a cell is born.

        Sxyz means that if there are x or y or z live cells surrounding a live
        cell, it survives into the next turn.

        All other cells die.

        Parameters
        ----------
        born : int or list
            The number of live cells around a dead cell that will turn it into a
            live cell at the start of the next turn.
        survive : int or list
            The number of live cells around a live cell that will mean it
            continues to be a live cell at the start of the next turn.

        Returns
        -------
        None.

        """
        # Checking that self.born is going to be what we expect it to be later.
        if isinstance(born, list):
            self.born = born
        elif isinstance(born, int):
            self.born = [born]
        else:
            raise TypeError(("The type of born in Grid.set_rules() is invalid. "
                             "It should be a list or an integer."))
        # Repeat for self.survive.
        if isinstance(survive, list):
            self.survive = survive
        elif isinstance(survive, int):
            self.survive = [survive]
        else:
            raise TypeError(("The type of survive in Grid.set_rules() is "
                             "invalid. It should be a list or an integer."))

    def get_rules(self):
        """Return the rules as a string in the standard B/S notation."""
        # Convert each element in self.born into a string then concatenate
        born = "".join(map(str, self.born))
        survive = "".join(map(str, self.survive))
        return f"B{born}/S{survive}"

    def set_neighbourhood_type(self, neighbourhood_type):
        """
        Set the neighbourhood type for the cell rules.

        The possible neighbourhoods are Moore and vonNeumann neighbourhoods.
        The neighbourhood refers to which cells are used for updating the
        central cell.

        Parameters
        ----------
        neighbourhood_type : string (case insensitive)
            The neighbourhood type, either 'Moore' or 'vonNeumann'.

        Returns
        -------
        None.

        """
        if isinstance(neighbourhood_type, str):
            self.neighbourhood_type = neighbourhood_type.lower()
        else:
            raise TypeError(("set.neighbourhood_type() has been passed a value "
                            f"that is a {type(neighbourhood_type)} as opposed "
                             "to a string."))

        # Check that it is one of the allowed values, moore or vonneumann.
        if self.neighbourhood_type not in ["moore", "vonneumann"]:
            raise ValueError(("self.neighbourhood_type has an invalid value. "
                              "It should either be vonNeumann or Moore "
                              "(case insensitive)."))

    def read_from_file(self, fname):
        """
        Open and read text file to generate starting grid.

        The file should use 0s for dead cells, 1s for live cells, and should be
        constant width

        Valid:
            00000
            01000
            00010

        Not Valid:
            00000
            00000
            00000


        Parameters
        ----------
        fname : string
            The file name.

        Returns
        -------
        None.

        """
        array = np.genfromtxt(fname, delimiter=1, dtype=int)
        self.centre_grid(array)

    def centre_grid(self, array):
        """
        Centre* an array on the grid.

        *centre as best we can, its not always possible to get it exactly
        centred, for example if the grid has 8 rows and the array has 3.

        Parameters
        ----------
        array : numpy array
            A numpy array where the entries are 0 or 1.

        Returns
        -------
        None.

        """
        h, w = array.shape
        hdiff = (self.height - h) // 2
        wdiff = (self.width - w) // 2

        for i in range(h):
            for j in range(w):
                self.grid[i + hdiff, j + wdiff] = int(array[i, j])

    def print_title(self):
        """
        Print a title screen.

        The title screen says 'Conway's Game of Life' or 'GoL' depending on
        the size of the grid used.

        Returns
        -------
        None.

        """
        if self.width >= 14 and self.height >= 5:
            self._print_title_big()
        else:
            self._print_title_small()

    def _print_title_big(self):
        """Print a larger version of the title screen, for a normal grid."""
        # Top bar.
        print("—" * (self.width + 2))

        # Blank space, and the walls to left and right.
        for i in range((self.height - 3)//2):
            print("|" + ' '*self.width + "|")

        # The main text, centred on the grid.
        print("|" + f"""{"Conway's":^{self.width}s}""" + "|")
        print(f"|{' ':{self.width}}|")
        print("|" + f"{'Game of Life':^{self.width}s}" + "|")

        # Rest of the blank space, then the bottom bar.
        for i in range((self.height - 3)//2):
            print("|" + ' '*self.width + "|")
        print("—" * (self.width + 2))

    def _print_title_small(self):
        """Print a smaller version of the title screen, for a small grid."""
        # Top bar.
        print("—" * (self.width + 2))

        # Blank space, and the walls to left and right.
        for i in range((self.height - 1)//2):
            print("|" + ' '*self.width + "|")

        # The main text, centred on the grid.
        print("|" + f"{'G o L':^{self.width}s}" + "|")

        # Rest of the blank space, then the bottom bar.
        for i in range((self.height - 1)//2):
            print("|" + ' '*self.width + "|")
        print("—" * (self.width + 2))

    def __str__(self):
        """
        Create a string representation of the grid, to print to terminal.

        Bounds the grid with em-dashes '—' (not hyphens) and pipes '|'.
        This is so `print(grid_instance)` provides a nice output.
        The functionality should also extend to saving a pretty version of the
        grid to a file.
                                          ——————
                     0000                 |    |
        A grid like: 0101 is returned as: | █ █|
                     0110                 | ██ |
                     1001                 |█  █|
                                          ——————
        """
        top = bottom = "—" * (self.width + 2)
        top += "\n"
        for i in range(self.height):
            # Other potential symbols: ○, █, ▢, ■, ⚫, ⚪
            top += f"|{''.join(['█' if x else ' ' for x in self.grid[i]])}|\n"
        return top + bottom

    def _view(self, i, j):
        """Return the view of the cell & neighbourhood, and the cell value."""
        if self.neighbourhood_type == "vonneumann":
            cols = np.mod([i, i, i, i-1, i+1], self.height)
            rows = np.mod([j-1, j, j+1, j, j], self.width)

            view = self.grid[cols, rows]
            cell = view[1]

        elif self.neighbourhood_type == "moore":
            cols = np.mod([i-1, i, i+1], self.height)
            rows = np.mod([j-1, j, j+1], self.width)

            view = self.grid[np.ix_(cols, rows)]
            cell = view[1, 1]

        else:
            raise ValueError(("self.neighbourhood_type has an invalid value. "
                              "It should either be vonNeumann or Moore "
                              "(case insensitive)."))
        return view, cell

    def _update_cell(self, i, j):
        """
        Update cell (i, j) using the three rules, assuming grid is toroidal.

        The three default rules are: a live cell with 2 or 3 neighbours lives.
        A dead cell with 3 living neighbours becomes a live cell. Any other cell
        dies or stays dead.
        These numbers can be changed using the set_rules() function.

        A toroidal grid (or periodic boundary conditions) means that a cell on
        the far right hand side is next to a cell on the far left hand side in
        the same row. The same is true of the top and bottom rows, for cells
        in the same column.

        Parameters
        ----------
        i : int
            The row of the cell (y-coordinate).
        j : int
            The column of the cell (x-coordinate).

        Returns
        -------
        status : int
            The status (0 for dead, 1 for alive) of the cell at the start of
            the next timestep.

        """
        # create a view of the array, consisting of the cell (i, j), and each
        # of its neighbouring cells, applying periodic boundary conditions.
        view, cell_value = self._view(i, j)

        neighbour_alive_count = np.count_nonzero(view) - cell_value

        # Apply rules, first for births, then survivors.
        # self.born/self.survive are lists of how many live cells must surround
        # the dead/live cell for it to be alive at the start of the next turn.
        if cell_value == 0 and neighbour_alive_count in self.born:
            return 1
        elif cell_value == 1 and neighbour_alive_count in self.survive:
            return 1
        else:
            return 0

    def update_grid(self):
        """Update the grid."""
        token_grid = np.empty_like(self.grid)
        for i in range(self.height):
            for j in range(self.width):
                token_grid[i, j] = self._update_cell(i, j)
        self.grid = token_grid

    def add_r_pentomino(self):
        """Put an R pentomino in the centre of the grid."""
        # Mid-point Height and Mid-point Width
        mh, mw = self.height // 2, self.width // 2

        # Central bar
        self.grid[mh - 1: mh + 2, mw] = 1, 1, 1

        # The two off-shoots
        self.grid[mh - 1, mw + 1] = self.grid[mh, mw - 1] = 1

    def add_glider(self):
        """Put a glider in the centre of the grid."""
        # Mid-point Height and Mid-point Width
        mh, mw = self.height // 2, self.width // 2

        # Central bar
        self.grid[mh + 1, mw - 1:mw + 2] = 1, 1, 1

        # The two off-shoots
        self.grid[mh, mw + 1] = self.grid[mh - 1, mw] = 1

    def all_dead_or_alive(self):
        """Return True if every cell is dead, or every cell is alive."""
        all_dead = np.count_nonzero(self.grid) == 0
        all_alive = np.count_nonzero(self.grid) == self.grid.size
        return all_dead or all_alive

    def iterate(self):
        """
        Update the grid and print to terminal.

        If self.clear is set to True, the terminal screen is cleared before
        printing the new grid.
        """
        self.update_grid()
        if self.clear:
            # Currently only tested on Windows 10 & WSL Ubuntu, no mac OS.
            os.system('cls' if os.name == 'nt' else 'clear')
        print(self)
        time.sleep(1 / self.fps)

    def run(self, niter=None):
        """
        Start playing the game of life.

        Start with the current grid attribute, updating either niter times,
        until the user interrupts the process, or until all the cells are
        alive or all the cells are dead.

        Parameters
        ----------
        niter : int, optional
            The number of iterations the game in run for. The default is None,
            meaning it runs until the user interrupts the process or all the
            cells are alive or all the cells are dead.

        Returns
        -------
        None.

        """
        self.print_title()
        time.sleep(1)

        if niter is None:
            while True:
                self.iterate()
                # Once the grid is all alive or dead, stop
                if self.all_dead_or_alive():
                    break
        else:
            for i in range(niter):
                self.iterate()
                if self.all_dead_or_alive():
                    break


def main():
    # Try to run it with a filename given as a command line argument
    if len(sys.argv) > 1:
        try:
            grid = Grid(fname=sys.argv[1])
            grid.run()
        except OSError:
            print(("That file cannot be found. "
                   "Please make sure you've spelt it right"))
    else:
        grid = Grid(random=True)
        grid.run()

if __name__ == "__main__":
    main()
