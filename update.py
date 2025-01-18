import os
import sys
import json
import argparse
import requests

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

DIFFICULTY_DICT = {
       "E": "Easy",      "M": "Medium",    "H": "Hard", 
         1: "Easy",        2: "Medium",      3: "Hard",
       "1": "Easy",      "2": "Medium",    "3": "Hard",
    "Easy": "Easy", "Medium": "Medium", "Hard": "Hard",
}

class LeetCodeRecord:
    def __init__(self, index, tc, sc):
        self.index = index
        self.name, self.difficulty = self.fetch_problem_info()
        self.tc = tc
        self.sc = sc

    def fetch_problem_info(self):
        name, difficulty = None, None
        r = requests.get("https://leetcode.com/api/problems/all")
        for p in r.json()["stat_status_pairs"]:
            if p["stat"]["frontend_question_id"] == self.index:
                name = p["stat"]["question__title"]
                difficulty = DIFFICULTY_DICT[p["difficulty"]["level"]]
                break
        return name, difficulty

    def body(self, topic, row):
        body = {
            "values": [[str(self.index), f"=HYPERLINK(\"{self.url}\", \"{self.name}\")", 
                self.difficulty, self.tc, self.sc]],
            "range":f"{topic}!A{row}:E{row}",
            "majorDimension": "ROWS",
        }
        return body

    @property
    def lname(self):
        return None if self.name is None else "-".join(self.name.lower().split(" "))

    @property
    def url(self):
        return None if self.lname is None else f"https://leetcode.com/problems/{self.lname}/description"

class LeetCodeUpdater:
    def __init__(self, parser, ssid, version=4, scopes=["https://www.googleapis.com/auth/spreadsheets"]):
        self.ssid = ssid
        self.version = version
        self.parser = parser
        self.sheet = None
        self.scopes = scopes

    def setup_sheet(self):
        creds = None
        sheet = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", self.scopes)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", self.scopes)
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as f:
                f.write(creds.to_json())
        try:
            service = build("sheets", f"v{self.version}", credentials=creds)
            sheet = service.spreadsheets()
        except HttpError as err:
            print(err)
        return sheet

    def fetch_topics(self):
        ret = []
        try:
            sheets = self.sheet.get(spreadsheetId=self.ssid).execute()["sheets"]
            sheets = sorted(sheets, key=lambda x: x["properties"]["index"])
            for s in sheets:
                ret.append(s["properties"]["title"])
        except HttpError as err:
            print(err)
            ret = None
        return ret

    def get_row(self):
        ret = None
        try:
            result = self.sheet.values().get(spreadsheetId=self.ssid, range=f"{self.args.topic}!G1").execute()
            values = result.get("values", [])
            ret = int(values[0][0]) + 2
        except HttpError as err:
            print(err)
        return ret

    def print_topics(self):
        print('""""""""""""""""""""""""""""""""""""')
        for i, topic in enumerate(self.topics):
            print(f"\t{i:}: {topic}")
        print('""""""""""""""""""""""""""""""""""""')

    def check_args(self):
        ret = True
        topic = " ".join(self.args.topic)
        if topic in self.topics:
            self.args.topic = topic
        elif topic.isnumeric() and int(topic) < len(self.topics):
            self.args.topic = self.topics[int(topic)]
        elif not topic.isnumeric() and topic not in self.topics:
            print(f"Unknown topic: {topic}.")
            ret = False
        else:
            print(f"Topic index out of bound, please refer to the following table:")
            self.print_topics()
            ret = False
        self.args.tc = " ".join(self.args.tc)
        self.args.sc = " ".join(self.args.sc)
        return ret

    def update(self, record):
        row = self.get_row()
        body = record.body(self.args.topic, row)
        try:
            result = self.sheet.values().update(spreadsheetId=self.ssid, range=f"{self.args.topic}!A{row}:E{row}", 
                valueInputOption="USER_ENTERED", body=body).execute()
            print(result)
        except HttpError as err:
            print(err)

    def main(self):
        self.sheet = self.setup_sheet()
        if self.sheet is None:
            print("Failed to setup spreadsheet API service.")
            return
        self.topics = self.fetch_topics()
        if self.topics is None:
            print("Failed to fetch topics from spreadsheets.")
            return
        self.args = self.parser.parse_args()
        if self.args.print:
            self.print_topics()
            return
        if not self.check_args():
            print("Argument check failed.")
            return
        record = LeetCodeRecord(self.args.number, self.args.tc, self.args.sc)
        self.update(record)

def parse_args():
    parser = argparse.ArgumentParser(description="Update LeetCode Record to GoogleSheet.")
    parser.add_argument("number", help="# of the problem", type=int)
    parser.add_argument("topic", nargs="+", help="topic of the problem")
    parser.add_argument("--tc", nargs="+", required=True, type=str)
    parser.add_argument("--sc", nargs="+", required=True, type=str)
    parser.add_argument("--name", nargs="+", help="name of the problem (optional)")
    parser.add_argument("-d", "--difficulty", choices=["E", "M", "H"], help="difficulty of the problem (optional)")
    parser.add_argument("-p", "--print", action="store_true", help="print the mapping for topic and id")
    return parser

if __name__ == "__main__":
    if not os.path.exists("ssid"):
        print("Please provide ssid file!")
        exit(1)
    with open("ssid", "r") as f:
        ssid = f.readline().strip("\n ")
    lcu = LeetCodeUpdater(parse_args(), ssid)
    lcu.main()
