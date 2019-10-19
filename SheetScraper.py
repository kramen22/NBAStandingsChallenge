import gspread
from gspread.models import Cell
from oauth2client.service_account import ServiceAccountCredentials
import requests
from lxml import html
from NBAUtilities import westTeamCodeAlphabetical, eastTeamCodeAlphabetical, Picker

# use creds to create a client to interact with the Google Drive API & retrieve sheet
scope = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
creds = ServiceAccountCredentials.from_json_keyfile_name('NBAStandingsChallenge-19456b5d8e4b.json', scope)
client = gspread.authorize(creds)

# retrieve standings from basketball reference
bballRefUrl = "https://www.basketball-reference.com/leagues/NBA_2020.html"
response = requests.get(url=bballRefUrl, allow_redirects=False)
response.raise_for_status()
if response.status_code != 200:
    print('Basketball Reference could not be reached.')
    exit

# create html tree
tree = html.fromstring(response.content)

# spreadsheet cells for east and west standings from bball ref
standingsCells = []

# team name to standing (from bball ref)
# convert to team code to standing to avoid
# string comparisons, after retrieving standings
# sort alphabetically to relate to codes
eastNameToStanding = {}
westNameToStanding = {}
eastCodeToStanding = {}
westCodeToStanding = {}

westRows = tree.xpath('//table[@id="confs_standings_W"]/tbody/tr[contains(@class, "full_table")]')
for i in range(len(westRows)):
    westrow = westRows[i]
    standingsCells.append(Cell(i + 3, 3, westrow[0].text_content()))
    westNameToStanding.update({westrow[0].text_content(): i})

eastRows = tree.xpath('//table[@id="confs_standings_E"]/tbody/tr[contains(@class, "full_table")]')
for i in range(len(eastRows)):
    eastrow = eastRows[i]
    standingsCells.append(Cell(i + 3, 5, eastrow[0].text_content()))
    eastNameToStanding.update({eastrow[0].text_content(): i})

codeIndex = 0
for key in sorted(westNameToStanding.keys()):
    westCodeToStanding.update({westTeamCodeAlphabetical[codeIndex]: westNameToStanding.get(key)})
    codeIndex += 1

codeIndex = 0
for key in sorted(eastNameToStanding.keys()):
    eastCodeToStanding.update({eastTeamCodeAlphabetical[codeIndex]: eastNameToStanding.get(key)})
    codeIndex += 1

# read in picks and create pickers consider caching in csv to 
# avoid tampering
pickers = []
sheet = client.open("2019-20 NBA Seed Pick-Ems").sheet1
pickerCells = sheet.range('C23:T32')
pickerCells.sort(key=lambda x: x.row)
pickerCells.sort(key=lambda x: x.col)
# incoming bull shit code, these indices are based entirely 
# on the spreadsheet so don't @ me
scoreCells = []
numPickers = 6
readerIndex = 0
numPicks = 8
ewOffset = 10
pickerOffset = 28
diffRowOffset = 25
for i in range(numPickers):
    # values for player object
    name = pickerCells[readerIndex].value
    column = pickerCells[readerIndex].col
    pickswest = {}
    pickseast = {}
    # skip name and "west" header
    readerIndex += 2
    for j in range(numPicks):
        pickswest.update({pickerCells[readerIndex + j].value: j})
        pickseast.update({pickerCells[readerIndex + j + ewOffset].value: j})
    picker = Picker(name, column, pickswest, pickseast)
    pickers.append(picker)
    picker.calculateScore(westCodeToStanding, eastCodeToStanding)
    for k in range(numPicks):
        scoreCells.append(Cell(diffRowOffset + k, picker.column + 2, 'W:' + str(picker.scoreW[k]) + ' E:' + str(picker.scoreE[k])))
    readerIndex += pickerOffset

# create the leaderboard cells
leaderboardCells = []
leaderboardColOffset = 8
leaderboardRowOffset = 3
leaderboardPlace = 0

pickers.sort(key=lambda x: x.totalScore)
for picker in pickers:
    leaderboardCells.append(Cell(leaderboardRowOffset + leaderboardPlace, leaderboardColOffset, picker.name))
    leaderboardCells.append(Cell(leaderboardRowOffset + leaderboardPlace, leaderboardColOffset + 1, str(picker.totalScore)))
    leaderboardPlace += 1

# write the cells to the sheet \o/
allCells = []
allCells.extend(standingsCells)
allCells.extend(scoreCells)
allCells.extend(leaderboardCells)
sheet.update_cells(allCells)