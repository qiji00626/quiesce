Empirical Game-Theoretic Analysis
=================================

[![build](https://github.com/egtaonline/quiesce/workflows/build/badge.svg)](https://github.com/egtaonline/quiesce/actions)

A command line tool for running egta on arbitrary simulators.

Setup
-----

```
pip install --user -U egta
```

Usage
-----

You need a set of supplementary files to actually run this.
These files describe the game that's going to be run, and the process of getting payoff data for each profile when requested.
This repository contains a sample simulator called `cdasim` that can be used for this purpose.
Below are some example uses

1. Perform the quiesce routine on a game that already has game data.
   One can also add noise to the payoffs for testing of equilibria procedures but this will just run it with no noise.

   ```bash
   egta quiesce game:game:cdasim/data_game.json
   ```

2. Perform the quiesce routine on a game that's defined by a command line simulator.
   This will get profile data by sampling from the cdasim python simulator.

   ```bash
   egta quiesce 'sim:game:cdasim/small_game.json,command:python3 cdasim/sim.py 1 --single'
   ```

   By default the quiesce routine only uses one payoff sample per profile.
   Adding `,count:<number>` to the description will help reduce the noise.

3. Perform the quiesce routine on a game that's defined by an EGTA Online zip file.
   This will get profile by calling the batch script from a zip file the same way as EGTA Online.
   To accomplish this, this repository has a zip scheduler that takes a zip file and schedules like EGTA Online does.

   ```bash
   egta quiesce zip:game:cdasim/small_game.json,zipf:cdasim/cdasim.zip
   ```

4. Perform the quiesce routine on a game with information on EGTA Online.
   The parameters specified here are for the same simulation that was uploaded there.

   ```bash
   egta quiesce eo:game:1466,mem:2048,time:60 --dpr buyers:2,sellers:2
   ```

   Note: This game has already been solved, so this call will only fetch the initial game and then solve it without scheduling more profiles.


Development
===========

`Makefile` has all of the relevant commands for settings up a development environment.
Typing `make` will print out everything it's setup to do.

`make setup` will do a best effort to setup an appropriate development environment.
The script requires a python interpreter that's at least version 3.5.
To specify a different interpreter than the default lookup on your path use `make setup PYTHON=<alternate-python>`, e.g. on many ubuntu systems you might need to run `make setup PYTHON=python3`.
