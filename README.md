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
The simulation is interactive; users select options to view standings, league stats, or team stats. They may also choose to sort the table by category

User chooses to view league standings:

<img width="588" height="153" alt="Screenshot 2026-01-02 120415" src="https://github.com/user-attachments/assets/f055b895-e35c-4f87-a4e9-966e7eb2d3c8" />

User chooses to view league statistics:

<img width="454" height="699" alt="Screenshot 2026-01-02 120435" src="https://github.com/user-attachments/assets/4f7cac85-3a54-4ddc-acb1-66f856b0ab99" />

User chooses to view individual team statistics:

<img width="424" height="106" alt="Screenshot 2026-01-02 120450" src="https://github.com/user-attachments/assets/799a4abb-202c-41fb-a127-97433b0d0e16" />



