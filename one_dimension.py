# A simple cellular automaton based on simple rules.
# The number of iterations is passed on the command line,
# Then the rule, which otherwise defaults to rule 90
import sys
import numpy as np

# --- Rules ---
# The rules are generated by giving each combination of a cell and its
# neighbours either 1 or 0. Since there are eight combos, we can refer to a set
# of rules using an 8-bit binary number, so Rule 1 would look like:
#     |111|110|101|100|011|010|001|000|
#     | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
# And rule 90, the default as it generates a fractal, looks like:
#     |111|110|101|100|011|010|001|000|
#     | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 0 |

def generate_rules(rule_num):
    """
    Generate the rules that govern how the cells are updated.

    Uses the notation that each possible set of rules is given as a string of
    8 0s and 1s, which means it can be represented with an integer from 0->255.

    """
    RULES = {}
    keys = ["111", "110", "101", "100", "011", "010", "001", "000"]
    # Convert the rule into a binary string
    outcomes = [int(x) for x in f"{rule_num:08b}"]

    for key, value in zip(keys, outcomes):
        RULES[key] = value

    return RULES

# --- Printing nicely ---
def pprint(array):
    """Prints a nice version of the grid to the terminal."""
    height, width = array.shape
    print("—" * (width + 4))
    for i in range(height):
        print("|", "".join(['█' if x else ' ' for x in array[i]]), "|")
    print("—" * (width + 4))


def main():
    # Number of iterations, from command line
    try:
        niter = int(sys.argv[1])
    except IndexError:
        niter = int(input("How many iterations would you like to run?\n"))
    # Which rule number, if none given defaults to rule 90
    try:
        rule_num = int(sys.argv[2])
    except IndexError:
        rule_num = 90

    RULES = generate_rules(rule_num)

    # After N iterations, the width will be 1 + 2*N
    fwidth = 1 + 2 * niter

    # First axis is 'time', second is position
    grid = np.zeros((niter, fwidth), dtype=int)

    # Initial conditions, would be good to allow this to change, like reading
    # in from a file. But then I would need to change the boundaries.
    grid[0, niter] = 1

    for i in range(1, niter):
        for j in range(niter-i, niter+i+1):
            # Currently the boundaries are just one either side of the centre
            # to begin with, then two either side, then 3, 4, ...
            # This is better than considering the whole row of zeros I think,
            # because then the pattern grows.
            rule = "".join(grid[i-1, j-1:j+2].astype(str))
            grid[i, j] = RULES[rule]

    pprint(grid)

main()
