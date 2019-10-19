import gspread
from gspread.models import Cell as Cell
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

if response.status_code != requests.codes.ok:
    print('Basketball Reference could not be reached.')
    exit

tree = html.fromstring(response.content)
standingsCellsToUpdate = []

# team name to standing (from bball ref)
eastNameToStanding = {}
westNameToStanding = {}
# team code to standing, this is so at the end of the season
# when bball ref starts appending "*" to teams that clinch 
# playoff slots we don't have to rely on string comparisons
eastCodeToStanding = {}
westCodeToStanding = {}

westRows = tree.xpath('//table[@id="confs_standings_W"]/tbody/tr[contains(@class, "full_table")]')
for i in range(len(westRows)):
    westrow = westRows[i]
    standingsCellsToUpdate.append(Cell(i + 3, 3, westrow[0].text_content()))
    westNameToStanding.update({westrow[0].text_content(): i})

eastRows = tree.xpath('//table[@id="confs_standings_E"]/tbody/tr[contains(@class, "full_table")]')
for i in range(len(eastRows)):
    eastrow = eastRows[i]
    standingsCellsToUpdate.append(Cell(i + 3, 5, eastrow[0].text_content()))
    eastNameToStanding.update({eastrow[0].text_content(): i})

# iterate over east and west sorted alphabetically and push
# dictionary values to code to standings dictionary, because 
# both this and the arrays defined in utils are sorted 
# alphabetically by team name, there are no string comparisons 
# that need to be done (see line 29)
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
picker_cells = sheet.range('C23:T32')
picker_cells.sort(key=lambda x: x.row)
picker_cells.sort(key=lambda x: x.col)
# incoming bull shit code, these indices are based entirely 
# on the spreadsheet so don't @ me
num_pickers = 6
reader_index = 0
num_picks = 8
east_west_offset = 10
picker_offset = 28
for i in range(num_pickers):
    # values for player object
    name = picker_cells[reader_index].value
    column = picker_cells[reader_index].col
    pickswest = {}
    pickseast = {}
    # skip name and "west" header
    reader_index += 2
    for j in range(num_picks):
        pickswest.update({picker_cells[reader_index + j].value: j})
        pickseast.update({picker_cells[reader_index + j + east_west_offset].value: j})
    pickers.append(Picker(name, column, pickswest, pickseast))
    reader_index += picker_offset

# create the cells with updated pick differentials
scoreCellsToUpdate = []
leaderboardCellsToUpdate = []

row_offset = 25
for picker in pickers:
    picker.calculateScore(westCodeToStanding, eastCodeToStanding)
    for i in range(num_picks):
        scoreCellsToUpdate.append(Cell(row_offset + i, picker.column + 2, 'W:' + str(picker.scoreW[i]) + ' E:' + str(picker.scoreE[i])))

# create the leaderboard cells
leaderboard_column_offset = 8
leaderboard_row_offset = 3
leaderboardPlace = 0

pickers.sort(reverse=True, key=lambda x: x.totalScore)
for picker in pickers:
    leaderboardCellsToUpdate.append(Cell(leaderboard_row_offset + leaderboardPlace, leaderboard_column_offset, picker.name))
    leaderboardCellsToUpdate.append(Cell(leaderboard_row_offset + leaderboardPlace, leaderboard_column_offset + 1, str(picker.totalScore)))
    leaderboardPlace += 1

# write the cells to the sheet \o/
sheet.update_cells(standingsCellsToUpdate)
sheet.update_cells(scoreCellsToUpdate)
sheet.update_cells(leaderboardCellsToUpdate)