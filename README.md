# Legends Season Sim

## Overview
Legends Season Sim is an interactive hockey season simulator that generates player statistics and calculates team outcomes such as wins, losses, and standings. The project was built to practice Python fundamentals and explore basic data analysis with pandas. Users can run different components of the simulation through a simple main menu interface.

---

## Features
- Simulates player statistics across a season
- Calculates team wins, losses, and ties based on player ratings
- Uses pandas for structured data handling
- Interactive main function with user input options

---

## Technologies Used
- Python
- pandas
- NumPy

---

## How It Works
1. Player scoring is generated using probabilistic methods.
2. Using player scoring, a random amount of assists are generated for the team. These assists are divided based on player rating
3. Total league scoring is calculated, and goals against are divided amongst teams based on their defensive rating as a group
4. Goals against per game for each team are divided based on typical goal distrubutions in the NHL
5. Wins and losses are calculated based on a comparison for goals for per game, and goals against per game

Because the simulation includes randomness, results vary on each run.

---

## Example Output

  Team  Wins  Losses  Ties  Points  Goals For  Goals Against  Goal Differential
0  MTL    15       5     5      35        105             65                 40
1  DET    16       8     1      33        105             63                 42
2  PIT    14       8     3      31         88             90                 -2
3  BOS    14       9     2      30         88             92                 -4
4  EDM    11       7     7      29        116             80                 36
5  CHI    13      10     2      28         87             95                 -8
6  TOR    11      13     1      23         81            129                -48
7  FLA     8      11     6      22         70            126                -56

                 Name  Goals  Assists  Points  Points Per Game
0         Gordie Howe     35       47      82             3.28
1      Connor McDavid     30       45      75             3.00
2       Wayne Gretzky     33       41      74             2.96
3     Maurice Richard     27       38      65             2.60
4       Mario Lemieux     34       29      63             2.52
5           Bobby Orr     24       39      63             2.52
6        Jaromir Jagr     26       34      60             2.40
7     Auston Matthews     27       31      58             2.32
8     Niklas Lidstrom     24       34      58             2.32
9         Paul Coffey     20       37      57             2.28
10      Steve Yzerman     19       38      57             2.28
11      Jean Beliveau     21       34      55             2.20
12       Duncan Keith     19       36      55             2.20
13     Darryl Sittler     24       29      53             2.12
14       Howie Morenz     24       28      52             2.08
15         Bobby Hull     25       26      51             2.04
16     Larry Robinson     19       31      50             2.00
17      Sidney Crosby     16       33      49             1.96
18       Patrick Kane     18       31      49             1.96
19    Matthew Tkachuk     20       26      46             1.84
20        Ray Bourque     22       23      45             1.80
21       Mark Messier     22       21      43             1.72
22        Stan Mikita     18       24      42             1.68
23        Mats Sundin     20       21      41             1.64
24  Aleksander Barkov     17       23      40             1.60
25       Sam Reinhart     18       21      39             1.56
26        Ted Lindsay     25       14      39             1.56
27   Patrice Bergeron     14       24      38             1.52
28       Johnny Bucyk     14       23      37             1.48
29       Aaron Ekblad     10       25      35             1.40
30      Borje Salming      6       27      33             1.32
31      Phil Esposito     14       15      29             1.16
32      Chris Pronger     11       13      24             0.96
33      Chris Chelios      7       17      24             0.96
34        Doug Harvey     14       10      24             0.96
35        Kris Letang      5       13      18             0.72
36       Larry Murphy      7        5      12             0.48
37       Keith Yandle      5        1       6             0.24
38         Tim Horton      4        0       4             0.16
39          Red Kelly      2        0       2             0.08

             Name  Goals  Assists  Points  Points Per Game
0   Wayne Gretzky     33       41      74             2.96
1  Connor McDavid     30       45      75             3.00
2    Mark Messier     22       21      43             1.72
3     Paul Coffey     20       37      57             2.28
4   Chris Pronger     11       13      24             0.96

The simulation is interactive; users select options to view standings, league stats, or team stats.

