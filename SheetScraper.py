import gspread
from gspread.models import Cell as Cell
from oauth2client.service_account import ServiceAccountCredentials
import requests
from lxml import html
from NBAUtilities import spreadsheetHeaderEast, spreadsheetHeaderWest

# use creds to create a client to interact with the Google Drive API & retrieve sheet
scope = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
creds = ServiceAccountCredentials.from_json_keyfile_name('NBAStandingsChallenge-19456b5d8e4b.json', scope)
client = gspread.authorize(creds)
sheet = client.open("NBA Standings Challenge").sheet1

# retrieve standings from basketball reference
bballRefUrl = "https://www.basketball-reference.com/leagues/NBA_2019_standings.html"
response = requests.get(url=bballRefUrl, allow_redirects=False)
response.raise_for_status()

if response.status_code != requests.codes.ok:
    print('Basketball Reference could not be reached.')
    exit

tree = html.fromstring(response.content)

cellsToUpdate = []
# print east stats to sheet
eastRows = tree.xpath('//table[@id="confs_standings_E"]/tbody/tr[contains(@class, "full_table")]')
for i in range(len(spreadsheetHeaderEast)):
    cellsToUpdate.append(Cell(1, i + 1, spreadsheetHeaderEast[i]))
for i in range(len(eastRows)):
    row = eastRows[i]
    for j in range(len(row)):
        cellsToUpdate.append(Cell(i + 2, j + 1, row[j].text_content()))

westRows = tree.xpath('//table[@id="confs_standings_W"]/tbody/tr[contains(@class, "full_table")]')
for i in range(len(spreadsheetHeaderWest)):
    cellsToUpdate.append(Cell(1, i + 10, spreadsheetHeaderWest[i]))
for i in range(len(westRows)):
    row = westRows[i]
    for j in range(len(row)):
        cellsToUpdate.append(Cell(i + 2, j + 10, row[j].text_content()))

sheet.update_cells(cellsToUpdate)