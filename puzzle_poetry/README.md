## Overview

This repository accompanies Puzzle Poetry, an article in submission with the Journal of Wordplay Issue #5.

The `main.py` script takes two integer time periods and computes a time-step that would allow for splitting the time periods into rearrangably similar sequences.

## Usage

You can run the script from the command line using the following command:

```bash
python main.py --days [5,2] --verbose False
```

Replace `[5,2]` with your desired number of days and `False` with your desired verbosity setting.

## Dependencies

This script uses the `fire` library for command line interfaces. You can install it using pip:

```bash
pip3 install fire
```
