# teams
eastTeamCodeAlphabetical = [
    'ATL',
    'BKN',
    'BOS',
    'CHA',
    'CHI',
    'CLE',
    'DET',
    'IND',
    'MIA',
    'MIL',
    'NYK',
    'ORL',
    'PHI',
    'TOR',
    'WAS',
]

westTeamCodeAlphabetical = [
    'DAL',
    'DEN',
    'GSW',
    'HOU',
    'LAC',
    'LAL',
    'MEM',
    'MIN',
    'NOP',
    'OKC',
    'PHX',
    'POR',
    'SAC',
    'SAS',
    'UTA',
]

class Picker:
    def __init__(self, name, column, picksWest, picksEast):
        self.name = name
        self.column = column
        self.picksWest = picksWest
        self.picksEast = picksEast
        self.scoreE = []
        self.scoreW = []
        self.totalScore = 0

    def calculateScore(self, standingsW, standingsE):
        pickedStanding = 0
        for key in self.picksWest.keys():
            actualStanding = standingsW.get(key)
            self.scoreW.append(self.calculateDifference(pickedStanding, actualStanding))
            pickedStanding += 1
        pickedStanding = 0
        for key in self.picksEast.keys():
            actualStanding = standingsE.get(key)
            self.scoreE.append(self.calculateDifference(pickedStanding, actualStanding))
            pickedStanding += 1
        self.totalScore = sum(self.scoreE) + sum(self.scoreW)

    def calculateDifference(self, pickedStanding, actualStanding):
        difference = 0
        if(actualStanding > pickedStanding):
            difference = actualStanding - pickedStanding
        else:
            difference = pickedStanding - actualStanding
        if(actualStanding > 7):
            difference += 3
        return difference
