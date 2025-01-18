# leetcode-record

A python script to send problem name, link, difficulty, time/space complexity and topic to a Google sheet.

## Prerequisites

* Follow [this link](https://developers.google.com/workspace/guides/get-started) to create a Google Cloud Project and enable Google sheets API
* Create a spreadsheet and add it to the project, copy the spreadsheet ID to file ``ssid``
* ``python3 -m pip install -r requirements.txt``

## Format of Sheet

### v1

A spreadsheet consists of multiple sheets, one sheet per topic.

![截圖 2025-01-18 下午12.05.38](/Users/James/Desktop/screenshot/截圖 2025-01-18 下午12.05.38.png)

The format of each sheet looks like:

|       |            A |          B |          C |    D | E    |  F   |    G |
| :---: | -----------: | ---------: | ---------: | ---: | ---- | :--: | ---: |
| **1** | Problem Name | Problem ID | Difficulty |   TC | SC   | Note |    2 |
| **2** |      Two Sum |          1 |       Easy |    N | N    | ...  |      |
| **3** |          ... |          2 |        ... |  ... | ...  | ...  |      |
| **4** |              |            |            |      |      |      |      |

Here's how my sheet looks like:

![截圖 2025-01-18 下午12.41.07](/Users/James/Desktop/screenshot/截圖 2025-01-18 下午12.41.07.png)

* Row 1 serves as header.
* Column G is only used in row 1, indicating the amount of records in this sheet.

## Usage

``python3 update.py [Problem ID] [Topic] --tc [TC] --sc [SC]``

## v1

* The script should be executed once per record
* CLI only
* Must provide: 
  * problem ID, to fetch Problem name, problem link and difficulty from LeetCode
  * topic, since a problem could have several solutions and each solution could belong to different topic, it seems reasonable to provide the topic of your "own solution"
  * time/space complexity, have no idea on how to fetch complexity on LeetCode
* Must create the sheet for the topic manually in advance

## v2 plan

* Spreadsheet/sheet creation
* Executed once for multiple records
* Add GUI
* Reorganize sheet?
  * Some problems may be involved in more than 1 topic, e.g., [432. All O`one Data Structure](https://leetcode.com/problems/all-oone-data-structure/)
  * First, add all problems to a generic sheet and add a column "topics" and fetch topics from LeetCode
  * Then, in sheet for each topic, use FILTER to filter out the problems without the topic