import gspread
from gspread_dataframe import get_as_dataframe
from oauth2client.service_account import ServiceAccountCredentials
import random
import pandas as pd
import numpy as np

SEASON_LENGTH = 25  # Number of games in the season
attributes_dict = {}  # DataFrame to hold all team attributes


'''Gets the spreadsheet data from Google Sheets and returns it as a DataFrame'''
def import_workbook():
    #Define the scope (Google Sheets + Google Drive access)
    scope = ["https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"]

    #Load credentials file (JSON file)
    creds = ServiceAccountCredentials.from_json_keyfile_name(r"C:\Users\reidb\OneDrive\Documents\season-sim-101861c3a56d.json", scope)


    #Authorize the client
    client = gspread.authorize(creds)

    #Open sheet by name
    workbook = client.open("Legends Season Sim")

    #Get all the teams worksheets except for goalies and puts them in a data frame
    for ws in workbook.worksheets():
        if ws.title != "Goalies":
            players_df = get_as_dataframe(ws)
            players_df.dropna(how="all", inplace=True)  # Drop rows where all values are NaN
            players_df.dropna(axis=1, how="all", inplace=True)  # Drop columns where all values are NaN
            attributes_dict[ws.title] = players_df

    #Get the goalies worksheet
    goalies_worksheet = workbook.worksheet("Goalies") # Get the goalies worksheet
    goalies_df = get_as_dataframe(goalies_worksheet)
    #Drop empty rows/columns
    goalies_df.dropna(how="all", inplace=True)  # Drop rows where all values are NaN
    goalies_df.dropna(axis=1, how="all", inplace=True)  # Drop columns where all values are NaN

    return attributes_dict, goalies_df




class Team:
    def __init__(self, team_name, points_df):
        self.team_name = team_name
        self.points_df = pd.DataFrame(points_df).copy()

    '''Gets the team's name'''
    def get_name(self):
        return self.team_name
    
    def get_points_df(self):
        return self.points_df
    
    '''Gets the goalies dataframe'''
    def goalies_df(self, goalies_df):
        return goalies_df

    '''Gets the team's worksheet that was chosen and turns it into a dataframe'''
    def players_df(self, attributes_dict):
        players_df = attributes_dict[self.team_name] 
        return players_df
    

    '''Calculates the average skill of a given category for each player. 
    Example categories: 'Shooting', 'Passing', 'Defense' '''
    def average_skill(self, players_df, category):
        
        #This is a list of each player's average skills based on the category chosen
        average_skills = []

        for index, row in players_df.iterrows():
            player_name = row['Name']

            # Determine which skills that will be used to find the average based on category chosen
            if category == 'shooting':
                skill = ['Wrist Shot Accuracy', 'Slap Shot Accuracy', 'Wrist Shot Power', 'Slap Shot Power', 'Offensive Awareness']
            elif category == 'passing':
                skill = ['Offensive Awareness', 'Passing', 'Puck Control', 'Speed']
            elif category == 'defence':
                skill = ['Defensive Awareness', 'Shot Blocking', 'Stick Checking', 'Body Checking']

            average_skill = row[skill].mean()

            # If the rating is less than 80, set it to 80
            if average_skill < 80:
                average_skill = 80
            # If the rating is more than 100, set it to 100
            elif average_skill > 100:
                average_skill = 100
            average_skills.append(average_skill)

            #Gets the team's average skill based on the averages of the individual players
            team_average_skills = sum(average_skills) / len(average_skills)
        
        return average_skills
    
    '''
    - probabilities is a list of lists
    - each inner list contains the probabilities (Type float, between 0 and 1) of scoring 0, 1, 2, 3, or 4+ goals for that player
    '''
    def shooting_probabilities(self, players_df, category, average_skills):
        probabilities = []
        
        # Rescale to a 0–1 range where:
        # 80 = 0.0 (low), 90 = 0.5 (average), 100 = 1.0 (elite)
        factor = []
        for player in average_skills:
            individual_factor = (player - 80) / (100 - 80)
            factor.append(individual_factor)

        for index, row in players_df.iterrows():

            if category == 'shooting':
                Fweights = [70, 20, 7, 2, 1]
                TWF_weights = [75, 18, 6, 1.5, 1]
                OFD_weights = [80, 15, 5, 1, 0.5]
                TWD_weights = [87, 8, 2, 1, 0.5]
                DFD_weights = [94, 5, 1.5, 1, 0.5]

                if row['Position'] == 'F': #the reason it isn't df['position'] == 'F' is because it would return a series, not a single value. Row resturns the row that it is currently on in the loop
                    if row['Player Type'] == 'TWF':
                        base_weights = TWF_weights
                    else:
                        base_weights = Fweights
                elif row['Position'] == 'D':
                    if row['Player Type'] == 'OFD':
                        base_weights = OFD_weights
                    elif row['Player Type'] == 'TWD' or row['Player Type'] == 'ENF':
                        base_weights = TWD_weights
                    elif row['Player Type'] == 'DFD':
                        base_weights = DFD_weights
                
                weights = [
                    base_weights[0] * (1 - factor[index]),     # chance of 0G drops as skill increases
                    base_weights[1] * (0.8 + factor[index]),   # chance of 1G increases slightly
                    base_weights[2] * (0.5 + factor[index]),   # 2G gets a good boost
                    base_weights[3] * (0.2 + factor[index]),   # 3G still uncommon
                    base_weights[4] * (0.1 + factor[index])    # 4+G rare even at high skill
                ]

                individual_probabilities = []
                total = sum(weights)
                for w in weights:
                    probability = w / total
                    individual_probabilities.append(probability)
                probabilities.append(individual_probabilities)

            else:
                print("Invalid category for shooting probabilities.")
        return probabilities


    '''Simulates the team's goals'''
    def sim_goals(self, players_df, points_df, shooting_probabilities):
        team_goals_per_player = []  # List to hold each player's goals per game
        for index, row in players_df.iterrows():
            name = row['Name']

             # Choose how many goals they score in each game based on the probabilities
            goal_options = [0, 1, 2, 3, 4]
            player_goals = [] #goals scored by game of each player

            for i in range(SEASON_LENGTH):
                goals = random.choices(goal_options, weights=shooting_probabilities[index])[0]
                player_goals.append(goals)
            
            team_goals_per_player.append(player_goals)  # Append the player's goals per game to the team list
            

            total_goals = sum(player_goals) #Sums all the goals in the season for that player
            
            points_df.loc[index, 'Name'] = name #if i do some sort of comination with loc[index], it basically highlights the row i currently am on in the loop
            points_df.loc[index, 'Goals'] = total_goals  # Add total goals to the points DataFrame
        
        points_df['Goals'] = points_df['Goals'].astype(int)  # Ensure Goals show up as integers in the DataFrame
        return team_goals_per_player #List of a list. Each inner list is a player's goals per game


    '''
    Each value in probabilities is the percentage chance (Type float, between 0 and 100) of that player getting an assist on a goal 
    '''
    def passing_probabilities(self, category, average_skills):

        probabilities = []
        
        # Rescale to a 0–1 range where:
        # 80 = 0.0 (low), 90 = 0.5 (average), 100 = 1.0 (elite)
        factor = []
        for player in average_skills:
            individual_factor = (player - 80) / (100 - 80)
            factor.append(individual_factor)
        
        #get the average factor for the team
        team_factor = sum(factor) / len(factor)
        
        #Gets the probabilities for each player to get an assist
        if category == 'passing':
            for value in factor:
                #calculates how much percent higher or lower the player's passing skill is compared to the team average
                diff = (value - team_factor) / team_factor * 100
                percentages = 50 + diff
                if percentages < 0:
                    percentages = 0
                elif percentages > 100:
                    percentages = 100
                probabilities.append(percentages)
        else:
            print("Invalid category for passing probabilities.")

        return probabilities

    '''Simulates the assists for the team based on total team assists and each player's passing probabilities'''
    def sim_assists(self, points_df, team_goals_per_player, passing_probabilities):
        
        #Gets the total number of goals that the team scored in the season
        total = 0
        for player in team_goals_per_player:
            total += sum(player)

        #Gets the total number of assists that the team made in the season
        assists_per_goal = []
        for i in range(total):
            assists_per_goal.append(random.choices([0, 1, 2], weights=[0.2, 0.25, 0.55])[0]) #Can either have 0, 1, or 2 total assist per goal. Weights are split up based on NHL percentages of how many goals have 0, 1, or 2 assists
        team_assists = sum(assists_per_goal) # Total assists by the team

        
        individual_assists = []

        for i in range(team_assists):
            assist_player = random.choices([0, 1, 2, 3, 4], weights=passing_probabilities)[0]  # Choose a player to get the assist based on their index number
            individual_assists.append(assist_player)

        #counhts how many assists each player has
        player_0_assists = individual_assists.count(0)
        player_1_assists = individual_assists.count(1)
        player_2_assists = individual_assists.count(2)
        player_3_assists = individual_assists.count(3)
        player_4_assists = individual_assists.count(4)

        index_list = [player_0_assists, player_1_assists, player_2_assists, player_3_assists, player_4_assists]
        points_df['Assists'] = index_list  # Add assists to the points DataFrame


    '''Calculates total points for each player and adds it to the points DataFrame. Also calculates points per game'''
    def add_points(self, points_df):
        points_df['Points'] = points_df['Goals'] + points_df['Assists'].astype(int)  # Calculate total points for each player, and ensures they are integers
        points_df['Points Per Game'] = points_df['Points'] / SEASON_LENGTH  # Calculate points per game


    '''Calculates the total goals scored by the team in each game of the season'''
    def goals_per_game(self,team_goals_per_player):
        total_goals_season = []
        for game in range(len(team_goals_per_player[0])):
            team_goals_per_game = []  # List to hold the team's goals for that game  
            for player in range(len(team_goals_per_player)):  
                team_goals_per_game.append(team_goals_per_player[player][game])
            goals_per_game = sum(team_goals_per_game)
            total_goals_season.append(goals_per_game)
        goals_for = sum(total_goals_season)

        # - total_goals_season is a list, which should be the length of the season, with each value being the total goals scored by the team in that game
        # - goals_for is the total number of goals scored by the team in the season
        return total_goals_season, goals_for 

    '''
    There is only one value in probabilities, which is the team's factor (Type float, between 0 and 1) as the probability as getting assigned a goal against
    '''
    def defence_probabilities(self, players_df, goalies_df, category, average_skills):

        # Rescale to a 0–1 range where:
        # 80 = 0.0 (low), 90 = 0.5 (average), 100 = 1.0 (elite)
        factor = []
        for player in average_skills:
            individual_factor = (player - 80) / (100 - 80)
            factor.append(individual_factor)

        if category == 'defence':
            for index, row in players_df.iterrows():

                # Adjust factor for each player based on position and player type
                if row['Position'] == 'F':
                    if row['Player Type'] == 'TWF':
                        factor[index] = factor[index] * 1.02
                elif row['Position'] == 'D':
                    if row['Player Type'] == 'OFD':
                        factor[index] = factor[index] * 0.98
                    elif row['Player Type'] == 'DFD':
                        factor[index] = factor[index] * 1.02
                
            goalie_row = goalies_df[goalies_df['Team'] == self.team_name]  # Find the row for the current team in the goalies DataFrame
            goalie_overall = goalie_row.iloc[0]['Overall']
            
            #get the average factor for the team
            team_factor = sum(factor) / len(factor)

            if goalie_overall == 99:
                team_factor = team_factor * 1.25
            elif goalie_overall == 98:
                team_factor = team_factor * 1.24
            elif goalie_overall == 97:
                team_factor = team_factor * 1.23
            elif goalie_overall == 96:
                team_factor = team_factor * 1.22
            elif goalie_overall == 95:
                team_factor = team_factor * 1.21
            elif goalie_overall == 94:
                team_factor = team_factor * 1.09
            elif goalie_overall == 93:
                team_factor = team_factor * 1.08
            elif goalie_overall == 92:
                team_factor = team_factor * 1.05
            elif goalie_overall == 91:
                team_factor = team_factor * 1.04
            elif goalie_overall == 90:
                team_factor = team_factor * 1.01
            elif goalie_overall == 89:
                team_factor = team_factor * 1.00
            elif goalie_overall == 88:
                team_factor = team_factor * 0.99
            elif goalie_overall == 87:
                team_factor = team_factor * 0.96
            elif goalie_overall == 86:
                team_factor = team_factor * 0.95
            elif goalie_overall == 85:
                team_factor = team_factor * 0.94
            elif goalie_overall == 84:
                team_factor = team_factor * 0.93
            else: 
                team_factor = team_factor * 0.92
                    

            if team_factor < 0:
                team_factor = 0
            elif team_factor > 1:
                team_factor = 1
                
            #Gets the inverse factor for defense, since a higher factor should mean less goals allowed
            inverse_factor = 1 - team_factor

            return inverse_factor
        else:
            print("Invalid category for defence probabilities.")
    
    '''Sims the goals against each game for the team based on the defence probabilities'''
    def sim_goals_against(self, i, goals_against):
        #Randomly assigns a value to each game that shows how many goals they are likely to give up that game
        #shape=2.0 shows how spiky things are. Lower number means more chaos, higher number means less chaos. This allows us to get some blowup games, but most of them are around the same value
        #scale=1.0 shows how spread out each blowup game is. Higher number means more extreme blowups, lower number means each score clusters closer to the same value
        weights = np.random.gamma(shape=1.8, scale=1.0, size=SEASON_LENGTH)

        probabilities = weights / weights.sum() # Normalize each weight to add up to 1, so they can be used as a "probability to get given a goal against this game"

        goals_against_by_game = np.random.multinomial(goals_against[i], probabilities).tolist()  # Simulate the goals against each game
        return goals_against_by_game #List of all the goals against per game for the team
    

    '''Calculates the team's record based on goals scored per game and goals against per game'''
    def team_record(self, total_goals_season, goals_against_by_game):
        wins = 0
        losses = 0
        ties = 0
        for game in range(SEASON_LENGTH):
            if total_goals_season[game] > goals_against_by_game[game]:
                wins += 1
            elif total_goals_season[game] < goals_against_by_game[game]:
                losses += 1
            else:
                ties += 1
            
        return wins, losses, ties

    '''Calculates the total points for the team based on wins and ties'''
    def points(self, wins, ties):
        return wins * 2 + ties * 1


'''Calculates each teams probability of getting assigned a goal against based on their defence factors'''
def goal_against_chance(defence_factor_list):
    defence_factor_sum = sum(defence_factor_list) # Calculate the total of the inverse factors
    chance_per_goal_against = []  # List to hold each team's chance of getting assigned a goal against
    for chance in defence_factor_list:
        percentage = (chance / defence_factor_sum)
        chance_per_goal_against.append(percentage)
    return chance_per_goal_against

'''Updates the standings dataframe with each team's stats'''
def update_standings(standings_df, each_team_name, each_team_goals, goals_against, wins_per_team, losses_per_team, ties_per_team, points_per_team):
    standings_df['Team'] = each_team_name
    standings_df['Goals For'] = each_team_goals
    standings_df['Goals Against'] = goals_against
    standings_df['Goal Differential'] = standings_df['Goals For'] - standings_df['Goals Against']
    standings_df['Wins'] = wins_per_team
    standings_df['Losses'] = losses_per_team
    standings_df['Ties'] = ties_per_team
    standings_df['Points'] = points_per_team

'''Runs the full season simulation'''
def run_sim():
    attributes_dict, goalies_df = import_workbook()
    points_df = {}  # Create an empty points dictionary to be used as a dataframe later

    EDM = Team("EDM", points_df)
    MTL = Team("MTL", points_df)
    DET = Team("DET", points_df)
    PIT = Team("PIT", points_df)
    TOR = Team("TOR", points_df)
    BOS = Team("BOS", points_df)
    FLA = Team("FLA", points_df)
    CHI = Team("CHI", points_df)


    teams = [EDM, MTL, DET, PIT, TOR, BOS, FLA, CHI]

    standings_df = pd.DataFrame(columns=['Team', 'Wins', 'Losses', 'Ties', 'Points', 'Goals For', 'Goals Against', 'Goal Differential'])

    league_goals = 0 #Total number of goals scored in the league in the season

    defence_factor_list = [] #List of each team's defence factor. Used to calculate how much above or below average each team's defence is later
    each_team_name = [] #List of each team's name
    each_team_goals = [] #List of each team's total goals scored in the season

    for team in teams:
        team_name = team.get_name()
        players_df = team.players_df(attributes_dict)
        goalies_df = team.goalies_df(goalies_df)
        points_df = team.get_points_df()

        #Gets each players goals for the season
        average_shooting = team.average_skill(players_df, 'shooting')
        shooting_probabilities = team.shooting_probabilities(players_df, 'shooting', average_shooting)
        team_goals_per_player = team.sim_goals(players_df, points_df, shooting_probabilities)

        #Gets each player's assists for the season
        average_passing = team.average_skill(players_df, 'passing')
        passing_probabilities = team.passing_probabilities('passing', average_passing)
        team.sim_assists(points_df, team_goals_per_player, passing_probabilities)

        #Calculates each player's total points for the season
        team.add_points(points_df)

        #Calculates the total goals scored by the team in each game of the season
        total_goals_season, goals_for = team.goals_per_game(team_goals_per_player)
        league_goals += goals_for

        #Calculates the team's defence factor
        average_defence = team.average_skill(players_df, 'defence')
        defence_probabilities = team.defence_probabilities(players_df, goalies_df, 'defence', average_defence)
        defence_factor_list.append(defence_probabilities)

        each_team_name.append(team_name)
        each_team_goals.append(goals_for)


    chance_per_goal_against = goal_against_chance(defence_factor_list)
    goals_against = np.random.multinomial(league_goals, chance_per_goal_against)  # Simulate the goals against for each team based on the probabilities
    goals_against = goals_against.tolist()  # Convert the numpy array to a list. This list contains each team's goals against for the season
 
    wins_per_team = []
    losses_per_team = []
    ties_per_team = []
    points_per_team = []

    for i, team in enumerate(teams):
        #Simulates goals against per game for each team
        goals_against_by_game = team.sim_goals_against(i, goals_against)

        #Calculates each team's record based on goals for and goals against per game
        wins, losses, ties = team.team_record(total_goals_season, goals_against_by_game)
        wins_per_team.append(wins)
        losses_per_team.append(losses)
        ties_per_team.append(ties)

        #Calculates each team's total points
        points = team.points(wins, ties)
        points_per_team.append(points)

    update_standings(standings_df, each_team_name, each_team_goals, goals_against, wins_per_team, losses_per_team, ties_per_team, points_per_team)
    return teams, standings_df

'''Displays the stats and allows the user to sort by different stats'''
def sort_stats(df):
    again = 'y'
    while again == 'y':
        print("Sort Options:\n1. Points\n2. Goals\n3. Assists\n4. Points Per Game\n")
        sort = int(input("Enter the number of the stat you want to sort by: "))
        if sort == 1:
            print(df.sort_values(by='Points', ascending=False).reset_index(drop=True))
        elif sort == 2:
            print(df.sort_values(by='Goals', ascending=False).reset_index(drop=True))
        elif sort == 3:
            print(df.sort_values(by='Assists', ascending=False).reset_index(drop=True))
        elif sort == 4:
            print(df.sort_values(by='Points Per Game', ascending=False).reset_index(drop=True))
        else:
            print("Invalid input. Try Again.")

        again = input("Sort Another Value? (y/n): ").strip().lower()
        if again == 'n':
            break



'''Displays the league points standings and allows different sorting by stats'''
def display_league_stats(teams):
    #Gets all the points dataframes from each team and combines them into one big dataframe
    league_points = []
    for team in teams:
        points_df = team.get_points_df()
        league_points.append(points_df)
    league_points_df = pd.concat(league_points, ignore_index=True)
    sort_stats(league_points_df)

'''Displays a specific team's stats and allows sorting by different stats'''
def display_team_stats(teams):
    valid_team = False
    while valid_team == False:
        team_choice = input("Enter the team you want to see stats for (PVW, BTH, RFH, LFS, BVS, AE, BII, BBB, HCR, HVH, LNN, RNS, ER, PTS, BTB, NVB): ").strip().upper()
        for team in teams:
            if team.get_name() == team_choice:
                points_df = team.get_points_df()
                sort_stats(points_df)
                valid_team = True
        if valid_team == False:
            print("Invalid team name. Please try again.")


'''Displays the league standings and allows sorting by different stats'''
def display_standings(standings_df):
    again = 'y'
    while again == 'y':
        print("Sort Options:\n1. Points\n2. Wins\n3. Goals For\n4. Goals Against\n5. Goal Differential\n")
        sort = int(input("Enter the number of the stat you want to sort by: "))
        if sort == 1:
            print(standings_df.sort_values(by='Points', ascending=False).reset_index(drop=True))
        elif sort == 2:
            print(standings_df.sort_values(by='Wins', ascending=False).reset_index(drop=True))
        elif sort == 3:
            print(standings_df.sort_values(by='Goals For', ascending=False).reset_index(drop=True))
        elif sort == 4:
            print(standings_df.sort_values(by='Goals Against', ascending=True).reset_index(drop=True))
        elif sort == 5:
            print(standings_df.sort_values(by='Goal Differential', ascending=False).reset_index(drop=True))
        else:
            print("Invalid input. Try Again.")
        
        again = input("Sort Another Value? (y/n): ").strip().lower()
        if again == 'n':
            print()
            break

def main():
    string = "Welcome to the Season Simulator!"
    border = '-' * len(string)
    print(f'{border}\n{string}\n{border}\n')
    print("Running Season Simulation...")
    teams, standings_df = run_sim()
    print("Complete!\n")

    #Loops through the options until the user wants to exit
    while True:
        print("Options:\n1. View League Standings\n2. View League Stats\n3. View Team Stats\n4. Exit\n")
        choice = int(input("Enter the number of the option you want to choose: "))
        if choice == 1:
            display_standings(standings_df)
        elif choice == 2:
            display_league_stats(teams)
        elif choice == 3:
            display_team_stats(teams)
        elif choice == 4:
            print("Thank you for using the Season Simulator!")
            break
        else:
            print("Invalid input. Try Again.")
    

if __name__ == "__main__":
    main()