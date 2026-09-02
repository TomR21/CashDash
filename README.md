# CashDash
Simple dashboarding tool to easily view all your assets and debts in a single place! Contains toggles for each asset, easy imports and the ability to add all sorts of investment vehicles. 




# Structure
The dashboard consist of 2 main categories: Assets and debts, just like a regular accounting spreadsheet. 

For both assets and debts, they are split into 3 different values: **Current value**, **amount of money put in** and **interest**. They are shown in table below. These are accumulated into a set time interval (year, month) and each value displays the cumulative amount of all time before until the starting date. 

Date | Current worth | Money put in | Interest |
|---|---|---|---|
| 01/01/2020  | €500  | €500  | €0  |
| 01/01/2021  | €605  | €600  | €5  |

Debts
Date | Current debt | Money put in | Interest |
|---|---|---|---|
| 01/01/2020  | €-1000  | €0  | €0  |
| 01/01/2021  | €-905  | €100  | €-5  |


# TODO
- Import current data
- Go from raw -> agg table per time interval per asset class
- Create combined asset class
- Create output values and charts
- - Optional: Add chart toggles per asset class

