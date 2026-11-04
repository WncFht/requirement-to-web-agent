# Ctrip travel services

A travel services application for account access, flight search and booking, and order management.

Dates and public countdowns use Asia/Shanghai and the shared application/evaluator clock 2026-07-19T08:00:00+08:00.

Sessions, current search criteria and booking selections are established by public UI behavior within each scenario, never injected into storage.

## REQ-1 Account access

Support enter the travel application, open password login, authenticate with password, end authenticated session.

**Type:** FOLDER
**Dependencies:** None

### REQ-1.1 Enter the travel application

Signed-out / displays exactly one Ctrip Travel heading and Log in link in Global navigation (a single named navigation landmark), a search box, and Origin and Destination textboxes. Fields have associated labels; controls may be buttons or links unless an explicit role is declared. Registration and SMS login are outside scope.

**IMG-INDEX · home**

![IMG-INDEX · home](reference/index.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-1.1-01 — Show signed-out entry
  - **Step:** STEP-REQ-1.1-01-01
    - **Given:** The visitor is signed out on the homepage; the benchmark clock is 2026-07-19 08:00 Asia/Shanghai.
    - **When:** Inspect the initial homepage.
    - **Then:** Exactly one Ctrip Travel heading and one Log in link in Global navigation are visible, together with the searchbox and Origin and Destination fields.
    - **References:** `\ref[image](IMG-INDEX)`

### REQ-1.2 Open password login

Log in in Global navigation opens a Log in heading, Account and Password fields, an initially unchecked Agree to terms checkbox and Log in submit button. Password login is the only required authentication method; registration, SMS and login-mode switching are outside scope.

**IMG-INDEX · home**

![IMG-INDEX · home](reference/index.png)

**IMG-LOGIN1 · login**

![IMG-LOGIN1 · login](reference/login1.png)

**IMG-LOGIN2 · login**

![IMG-LOGIN2 · login](reference/login2.png)

**Type:** ATOMIC
**Dependencies:** REQ-1.1

**Scenarios:**

- SCN-REQ-1.2-01 — Open password login
  - **Step:** STEP-REQ-1.2-01-01
    - **Given:** The visitor is signed out on the homepage; the benchmark clock is 2026-07-19 08:00 Asia/Shanghai.
    - **When:** Activate Log in within Global navigation.
    - **Then:** Log in heading, Account and Password fields are visible.
    - **References:** `\ref[requirement](REQ-1.1)`, `\ref[image](IMG-INDEX)`, `\ref[image](IMG-LOGIN1)`, `\ref[image](IMG-LOGIN2)`

### REQ-1.3 Authenticate with password

Users enter a verified mobile, username, or email in "Account"(role=textbox), enter "Password"(role=textbox), select the initially unchecked "Agree to terms"(role=checkbox), and click "Log in"(role=button). Agreement is required. Missing credentials or incorrect credentials show the specified alert without signing in; success returns home and replaces the login entry with "My account"(role=button).

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

**IMG-LOGIN1 · login**

![IMG-LOGIN1 · login](reference/login1.png)

**IMG-INDEX · home**

![IMG-INDEX · home](reference/index.png)

**Type:** ATOMIC
**Dependencies:** REQ-1.2

**Scenarios:**

- SCN-REQ-1.3-01 — Authenticate by email
  - **Step:** STEP-REQ-1.3-01-01
    - **Given:** The visitor is signed out on the homepage; the benchmark clock is 2026-07-19 08:00 Asia/Shanghai. Log in has been opened from Global navigation; Agree to terms initially is unchecked. ctrip_user@example.com is the verified user account.
      Seed prerequisites (prepared before this scenario):
      - existing verified accounts: {"user": {"email": "ctrip_user@example.com", "password": "Travel1234", "username": "ctrip_user", "mobile": "13800000010"}}
    - **When:** Enter Account ctrip_user@example.com and Password Travel1234, check Agree to terms and click Log in.
    - **Then:** Ctrip Travel homepage opens, My account is visible and the signed-out Log in navigation link disappears.
    - **References:** `\ref[requirement](REQ-1.2)`, `\ref[image](IMG-LOGIN1)`, `\ref[image](IMG-INDEX)`
- SCN-REQ-1.3-02 — Authenticate by username
  - **Step:** STEP-REQ-1.3-02-01
    - **Given:** The visitor is signed out on the homepage; the benchmark clock is 2026-07-19 08:00 Asia/Shanghai. Log in has been opened from Global navigation; Agree to terms initially is unchecked. ctrip_user identifies the verified user account.
      Seed prerequisites (prepared before this scenario):
      - existing verified accounts: {"user": {"email": "ctrip_user@example.com", "password": "Travel1234", "username": "ctrip_user", "mobile": "13800000010"}}
    - **When:** Enter Account ctrip_user and Password Travel1234, check Agree to terms and click Log in.
    - **Then:** Ctrip Travel homepage opens, My account is visible and the signed-out Log in navigation link disappears.
    - **References:** `\ref[requirement](REQ-1.2)`, `\ref[image](IMG-LOGIN1)`, `\ref[image](IMG-INDEX)`
- SCN-REQ-1.3-03 — Authenticate by mobile
  - **Step:** STEP-REQ-1.3-03-01
    - **Given:** The visitor is signed out on the homepage; the benchmark clock is 2026-07-19 08:00 Asia/Shanghai. Log in has been opened from Global navigation; Agree to terms initially is unchecked. 13800000010 belongs to the verified user account.
      Seed prerequisites (prepared before this scenario):
      - existing verified accounts: {"user": {"email": "ctrip_user@example.com", "password": "Travel1234", "username": "ctrip_user", "mobile": "13800000010"}}
    - **When:** Enter Account 13800000010 and Password Travel1234, check Agree to terms and click Log in.
    - **Then:** Ctrip Travel homepage opens, My account is visible and the signed-out Log in navigation link disappears.
    - **References:** `\ref[requirement](REQ-1.2)`, `\ref[image](IMG-LOGIN1)`, `\ref[image](IMG-INDEX)`
- SCN-REQ-1.3-04 — Reject missing account
  - **Step:** STEP-REQ-1.3-04-01
    - **Given:** The visitor is signed out on the homepage; the benchmark clock is 2026-07-19 08:00 Asia/Shanghai. Log in has been opened from Global navigation; Agree to terms initially is unchecked.
    - **When:** Leave Account empty, enter Password Travel1234, check Agree to terms and click Log in.
    - **Then:** Enter your account alert appears, Account remains visible and My account is absent.
    - **References:** `\ref[requirement](REQ-1.2)`, `\ref[image](IMG-LOGIN1)`, `\ref[image](IMG-INDEX)`
- SCN-REQ-1.3-05 — Reject missing password
  - **Step:** STEP-REQ-1.3-05-01
    - **Given:** The visitor is signed out on the homepage; the benchmark clock is 2026-07-19 08:00 Asia/Shanghai. Log in has been opened from Global navigation; Agree to terms initially is unchecked.
      Seed prerequisites (prepared before this scenario):
      - existing verified accounts: {"user": {"email": "ctrip_user@example.com", "password": "Travel1234", "username": "ctrip_user", "mobile": "13800000010"}}
    - **When:** Enter Account ctrip_user@example.com, leave Password empty, check Agree to terms and click Log in.
    - **Then:** Enter your password alert appears, Account remains visible and My account is absent.
    - **References:** `\ref[requirement](REQ-1.2)`, `\ref[image](IMG-LOGIN1)`, `\ref[image](IMG-INDEX)`
- SCN-REQ-1.3-06 — Reject incorrect password
  - **Step:** STEP-REQ-1.3-06-01
    - **Given:** The visitor is signed out on the homepage; the benchmark clock is 2026-07-19 08:00 Asia/Shanghai. Log in has been opened from Global navigation; Agree to terms initially is unchecked.
      Seed prerequisites (prepared before this scenario):
      - existing verified accounts: {"user": {"email": "ctrip_user@example.com", "password": "Travel1234", "username": "ctrip_user", "mobile": "13800000010"}}
    - **When:** Enter Account ctrip_user@example.com and Password WrongPass123, check Agree to terms and click Log in.
    - **Then:** Incorrect account or password alert appears, Account remains visible and My account is absent.
    - **References:** `\ref[requirement](REQ-1.2)`, `\ref[image](IMG-LOGIN1)`, `\ref[image](IMG-INDEX)`
- SCN-REQ-1.3-07 — Require legal acceptance
  - **Step:** STEP-REQ-1.3-07-01
    - **Given:** The visitor is signed out on the homepage; the benchmark clock is 2026-07-19 08:00 Asia/Shanghai. Log in has been opened from Global navigation; Agree to terms initially is unchecked.
      Seed prerequisites (prepared before this scenario):
      - existing verified accounts: {"user": {"email": "ctrip_user@example.com", "password": "Travel1234", "username": "ctrip_user", "mobile": "13800000010"}}
    - **When:** Enter Account ctrip_user@example.com and Password Travel1234, leave Agree to terms unchecked and click Log in.
    - **Then:** Agree to terms first alert appears, the login form remains visible and My account is absent.
    - **References:** `\ref[requirement](REQ-1.2)`, `\ref[image](IMG-LOGIN1)`, `\ref[image](IMG-INDEX)`

### REQ-1.4 End authenticated session

Hovering "My account"(role=button) reveals the Log out menuitem. Activating it clears the session and replaces My account with Log in on the signed-out homepage, including after reload.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

**IMG-ENTER-SELF · home**

![IMG-ENTER-SELF · home](reference/enter_self.png)

**Type:** ATOMIC
**Dependencies:** REQ-1.3

**Scenarios:**

- SCN-REQ-1.4-01 — Log out and retain signed-out state
  - **Step:** STEP-REQ-1.4-01-01
    - **Given:** The verified user has signed in through Account ctrip_user@example.com, Password Travel1234 and checked Agree to terms.
      Seed prerequisites (prepared before this scenario):
      - existing verified accounts: {"user": {"email": "ctrip_user@example.com", "password": "Travel1234", "username": "ctrip_user", "mobile": "13800000010"}}
    - **When:** Hover My account, activate Log out (menuitem), then reload.
    - **Then:** Log in returns to Global navigation and My account disappears, both before and after reload.
    - **References:** `\ref[requirement](REQ-1.3)`, `\ref[image](IMG-ENTER-SELF)`

## REQ-2 Find flights and select a fare

Support configure trip type, select and exchange route cities, choose valid journey dates, execute matching or empty flight search, carry traveler and cabin preferences into search, update results search criteria, filter flights by stops and airline, sort matching flights, inspect and collapse fare options, select the identified flight and fare, change route criteria on flight results, recover from an empty flight search, restore flights after removing nonstop filter, remove airline filter while keeping nonstop preference.

**Type:** FOLDER
**Dependencies:** None

### REQ-2.1 Configure trip type

"One way"(role=radio) is initially selected, with "Add return"(role=button) available and "Return date"(role=textbox) absent. Selecting "Round trip"(role=radio) reveals Return date, while returning to One way hides it. "Multi-city"(role=radio) is also available.

Multi-city is retained as capability context; its detailed behavior is unspecified.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

Dates and time-dependent behavior use Asia/Shanghai and the shared application/evaluator time 2026-07-19T08:00:00+08:00; public countdowns use elapsed time.

Published flight identity includes route, date and dataset. Flight identity includes origin, destination, date and flight number.

Multi-city, time-filter and airport-filter details are not specified beyond their capability context; the stated trip-type behaviors do not imply additional validation policies.

**IMG-SEARCH · home**

![IMG-SEARCH · home](reference/search.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-2.1-01 — Switch one-way and round-trip modes
  - **Step:** STEP-REQ-2.1-01-01
    - **Given:** The visitor is signed out on the homepage; the benchmark clock is 2026-07-19 08:00 Asia/Shanghai. One way is initially selected.
    - **When:** Inspect Add return and the absent Return date, select Round trip, then select One way again.
    - **Then:** Round trip reveals Return date; One way removes that field and restores Add return; Multi-city remains available.
    - **References:** `\ref[requirement](REQ-1.1)`, `\ref[image](IMG-SEARCH)`

### REQ-2.2 Select and exchange route cities

"Origin"(role=textbox) and "Destination"(role=textbox) accept cities; "Swap cities"(role=button) exchanges their values without searching. "City selection"(role=button) opens "City selection"(role=dialog), with its "City selection"(role=tab) choices: origin defaults to Popular with Chengdu, while the destination's GHIJ tab includes Guangzhou. Choosing a city closes the dialog and fills the city and airport code.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

Dates and time-dependent behavior use Asia/Shanghai and the shared application/evaluator time 2026-07-19T08:00:00+08:00; public countdowns use elapsed time.

Published flight identity includes route, date and dataset. Flight identity includes origin, destination, date and flight number.

**IMG-CITY-SELECTION · home**

![IMG-CITY-SELECTION · home](reference/city_selection.png)

**Type:** ATOMIC
**Dependencies:** REQ-1.1

**Scenarios:**

- SCN-REQ-2.2-01 — Exchange route cities
  - **Step:** STEP-REQ-2.2-01-01
    - **Given:** The visitor is signed out on the homepage; the benchmark clock is 2026-07-19 08:00 Asia/Shanghai.
    - **When:** Enter Origin Chengdu and Destination Guangzhou, then click Swap cities.
    - **Then:** Origin becomes Guangzhou and Destination becomes Chengdu.
    - **References:** `\ref[requirement](REQ-1.1)`, `\ref[image](IMG-CITY-SELECTION)`
- SCN-REQ-2.2-02 — Choose a popular origin
  - **Step:** STEP-REQ-2.2-02-01
    - **Given:** The visitor is signed out on the homepage; the benchmark clock is 2026-07-19 08:00 Asia/Shanghai.
    - **When:** Click Origin, inspect the selected Popular tab in City selection, then click Chengdu.
    - **Then:** Origin becomes Chengdu (CTU) and City selection closes.
    - **References:** `\ref[requirement](REQ-1.1)`, `\ref[image](IMG-CITY-SELECTION)`
- SCN-REQ-2.2-03 — Choose destination by pinyin group
  - **Step:** STEP-REQ-2.2-03-01
    - **Given:** The visitor is signed out on the homepage; the benchmark clock is 2026-07-19 08:00 Asia/Shanghai.
    - **When:** Click Destination, select GHIJ within City selection and click Guangzhou.
    - **Then:** Destination becomes Guangzhou (CAN) and City selection closes.
    - **References:** `\ref[requirement](REQ-1.1)`, `\ref[image](IMG-CITY-SELECTION)`

### REQ-2.3 Choose valid journey dates

Opening "Departure date"(role=textbox) displays a calendar with daily fares and full-date actions. "2026-07-21"(role=button) shows ¥460 and sets departure before closing; "2026-07-18"(role=button) is disabled because it precedes July 19. "Add return"(role=button) selects "Round trip"(role=radio) and opens "Return date"(role=textbox). Selecting "2026-07-25"(role=button) after July 21 displays a four-day trip, while "2026-07-20"(role=button) is disabled as a return before departure.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

Dates and time-dependent behavior use Asia/Shanghai and the shared application/evaluator time 2026-07-19T08:00:00+08:00; public countdowns use elapsed time.

Published flight identity includes route, date and dataset. Flight identity includes origin, destination, date and flight number.

**IMG-DATE-SELECTION · home**

![IMG-DATE-SELECTION · home](reference/date_selection.png)

**IMG-DATE-SELECTION-2 · home**

![IMG-DATE-SELECTION-2 · home](reference/date_selection_2.png)

**Type:** ATOMIC
**Dependencies:** REQ-1.1

**Scenarios:**

- SCN-REQ-2.3-01 — Select a future departure with fare
  - **Step:** STEP-REQ-2.3-01-01
    - **Given:** The visitor is signed out on the homepage; the benchmark clock is 2026-07-19 08:00 Asia/Shanghai. Calendar fares include ¥460 for July 21.
      Seed prerequisites (prepared before this scenario):
      - published booking inventory: {"flights": [{"number": "CZ3401", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "China Southern", "stops": "nonstop", "fare": 320, "departure": "11:00", "on_time": "95%"}, {"number": "JD5162", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "stopover", "fare": 460, "departure": "09:00", "on_time": "88%"}, {"number": "MU5234", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "nonstop", "fare": 580, "departure": "07:30", "on_time": "91%"}]}
    - **When:** Open Departure date, inspect the fare, then click 2026-07-21.
    - **Then:** ¥460 is displayed; Departure date becomes 2026-07-21 and the date picker closes.
    - **References:** `\ref[requirement](REQ-2.1)`, `\ref[image](IMG-DATE-SELECTION)`, `\ref[image](IMG-DATE-SELECTION-2)`
- SCN-REQ-2.3-02 — Disable past departure dates
  - **Step:** STEP-REQ-2.3-02-01
    - **Given:** The visitor is signed out on the homepage; the benchmark clock is 2026-07-19 08:00 Asia/Shanghai.
    - **When:** Open Departure date and inspect 2026-07-18.
    - **Then:** That past-date button is visible but disabled.
    - **References:** `\ref[requirement](REQ-2.1)`, `\ref[image](IMG-DATE-SELECTION)`, `\ref[image](IMG-DATE-SELECTION-2)`
- SCN-REQ-2.3-03 — Add a four-day return trip
  - **Step:** STEP-REQ-2.3-03-01
    - **Given:** The visitor is signed out on the homepage; the benchmark clock is 2026-07-19 08:00 Asia/Shanghai. Departure date has been selected as 2026-07-21.
    - **When:** Click Add return and select 2026-07-25.
    - **Then:** Round trip is selected, Return date becomes 2026-07-25 and 4 days is displayed.
    - **References:** `\ref[requirement](REQ-2.1)`, `\ref[image](IMG-DATE-SELECTION)`, `\ref[image](IMG-DATE-SELECTION-2)`
- SCN-REQ-2.3-04 — Disable return before departure
  - **Step:** STEP-REQ-2.3-04-01
    - **Given:** The visitor is signed out on the homepage; the benchmark clock is 2026-07-19 08:00 Asia/Shanghai. Departure date has been selected as 2026-07-21.
    - **When:** Click Add return and inspect return choice 2026-07-20.
    - **Then:** The earlier return-date button is visible but disabled.
    - **References:** `\ref[requirement](REQ-2.1)`, `\ref[image](IMG-DATE-SELECTION)`, `\ref[image](IMG-DATE-SELECTION-2)`

### REQ-2.4 Execute matching or empty flight search

Users fill "Origin"(role=textbox), "Destination"(role=textbox), and "Departure date"(role=textbox), then click "Search flights"(role=button). Flight results preserves criteria and shows "Flight list"(role=region); Chengdu–Guangzhou on July 21 contains exactly CZ3401, JD5162, and MU5234 with published booking inventory fare, airline, stops, departure, and on-time facts. Equal cities show Origin and destination cannot be the same. Beihai–Mars City on July 23 displays No flights found and Modify search.

Domestic and international route search use benchmark date 2026-07-19. Flight results expose a list with listitems named "Flight <number>".

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

Dates and time-dependent behavior use Asia/Shanghai and the shared application/evaluator time 2026-07-19T08:00:00+08:00; public countdowns use elapsed time.

Published flight identity includes route, date and dataset. Flight identity includes origin, destination, date and flight number.

**IMG-INDEX · home**

![IMG-INDEX · home](reference/index.png)

**IMG-SEARCH-RESULTS · flight_results**

![IMG-SEARCH-RESULTS · flight_results](reference/search_results.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.2, REQ-2.3

**Scenarios:**

- SCN-REQ-2.4-01 — Show matching published flights
  - **Step:** STEP-REQ-2.4-01-01
    - **Given:** The visitor is signed out on the homepage; the benchmark clock is 2026-07-19 08:00 Asia/Shanghai. published booking inventory contains the three July 21 Chengdu–Guangzhou flights.
      Seed prerequisites (prepared before this scenario):
      - published booking inventory: {"flights": [{"number": "CZ3401", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "China Southern", "stops": "nonstop", "fare": 320, "departure": "11:00", "on_time": "95%"}, {"number": "JD5162", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "stopover", "fare": 460, "departure": "09:00", "on_time": "88%"}, {"number": "MU5234", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "nonstop", "fare": 580, "departure": "07:30", "on_time": "91%"}]}
      - city directory: {"Chengdu": {"code": "CTU", "group": "Popular"}, "Guangzhou": {"code": "CAN", "group": "GHIJ"}}
    - **When:** Enter Origin Chengdu and Destination Guangzhou, choose Departure date 2026-07-21 and click Search flights.
    - **Then:** Flight results opens with exactly CZ3401, JD5162 and MU5234; Origin, Destination and Departure date retain Chengdu, Guangzhou and 2026-07-21.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[requirement](REQ-2.3)`, `\ref[image](IMG-INDEX)`, `\ref[image](IMG-SEARCH-RESULTS)`
- SCN-REQ-2.4-02 — Reject identical cities
  - **Step:** STEP-REQ-2.4-02-01
    - **Given:** The visitor is signed out on the homepage; the benchmark clock is 2026-07-19 08:00 Asia/Shanghai.
    - **When:** Enter Chengdu in both Origin and Destination and click Search flights.
    - **Then:** Origin and destination cannot be the same alert appears; editable search remains and Flight results does not open.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[requirement](REQ-2.3)`, `\ref[image](IMG-INDEX)`, `\ref[image](IMG-SEARCH-RESULTS)`
- SCN-REQ-2.4-03 — Show empty route result
  - **Step:** STEP-REQ-2.4-03-01
    - **Given:** The visitor is signed out on the homepage; the benchmark clock is 2026-07-19 08:00 Asia/Shanghai. No Beihai–Mars City flight is published for July 23.
      Seed prerequisites (prepared before this scenario):
      - published booking inventory: {"flights": [], "empty_query": {"origin": "Beihai", "destination": "Mars City", "date": "2026-07-23"}}
    - **When:** Enter Origin Beihai and Destination Mars City, select Departure date 2026-07-23 and click Search flights.
    - **Then:** Flight list has no flight listitems and displays No flights found with Modify search.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[requirement](REQ-2.3)`, `\ref[image](IMG-INDEX)`, `\ref[image](IMG-SEARCH-RESULTS)`

### REQ-2.5 Carry traveler and cabin preferences into search

Selecting "Traveling with children"(role=checkbox) carries that preference into Flight results as Children included. "Cabin class"(role=combobox) includes Economy and retains the chosen option during search.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

Dates and time-dependent behavior use Asia/Shanghai and the shared application/evaluator time 2026-07-19T08:00:00+08:00; public countdowns use elapsed time.

Published flight identity includes route, date and dataset. Flight identity includes origin, destination, date and flight number.

**IMG-INDEX · home**

![IMG-INDEX · home](reference/index.png)

**IMG-SEARCH-RESULTS · flight_results**

![IMG-SEARCH-RESULTS · flight_results](reference/search_results.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.4

**Scenarios:**

- SCN-REQ-2.5-01 — Search with children included
  - **Step:** STEP-REQ-2.5-01-01
    - **Given:** The visitor is signed out on the homepage; the benchmark clock is 2026-07-19 08:00 Asia/Shanghai.
      Seed prerequisites (prepared before this scenario):
      - published booking inventory: {"flights": []}
    - **When:** Check Traveling with children, then Enter Origin Chengdu and Destination Guangzhou, choose Departure date 2026-07-21 and click Search flights.
    - **Then:** Flight results displays Children included.
    - **References:** `\ref[requirement](REQ-2.4)`, `\ref[image](IMG-INDEX)`, `\ref[image](IMG-SEARCH-RESULTS)`
- SCN-REQ-2.5-02 — Choose Economy preference
  - **Step:** STEP-REQ-2.5-02-01
    - **Given:** The visitor is signed out on the homepage; the benchmark clock is 2026-07-19 08:00 Asia/Shanghai.
      Seed prerequisites (prepared before this scenario):
      - published booking inventory: {"flights": []}
    - **When:** Select Economy in Cabin class, then Enter Origin Chengdu and Destination Guangzhou, choose Departure date 2026-07-21 and click Search flights.
    - **Then:** Economy is selected and retained in Cabin class on Flight results.
    - **References:** `\ref[requirement](REQ-2.4)`, `\ref[image](IMG-INDEX)`, `\ref[image](IMG-SEARCH-RESULTS)`

### REQ-2.6 Update results search criteria

Flight results permits changing route criteria, "Departure date"(role=textbox), and "Cabin class"(role=combobox). "Update results"(role=button) after selecting July 22 and Economy retains the results view and updated criteria while refreshing "Flight list"(role=region) for that day.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

Dates and time-dependent behavior use Asia/Shanghai and the shared application/evaluator time 2026-07-19T08:00:00+08:00; public countdowns use elapsed time.

Published flight identity includes route, date and dataset. Flight identity includes origin, destination, date and flight number.

**IMG-SEARCH-PANEL · flight_results**

![IMG-SEARCH-PANEL · flight_results](reference/search_panel.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.4

**Scenarios:**

- SCN-REQ-2.6-01 — Refresh date and cabin on results
  - **Step:** STEP-REQ-2.6-01-01
    - **Given:** The visitor has used Origin Chengdu, Destination Guangzhou, Departure date 2026-07-21 and Search flights; Flight list contains CZ3401 (¥320, 11:00, 95%, nonstop), JD5162 (¥460, 09:00, 88%, stopover) and MU5234 (¥580, 07:30, 91%, nonstop). July 22 contains only CZ3401 at ¥320.
      Seed prerequisites (prepared before this scenario):
      - published booking inventory: {"flights": [{"number": "CZ3401", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "China Southern", "stops": "nonstop", "fare": 320, "departure": "11:00", "on_time": "95%"}, {"number": "JD5162", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "stopover", "fare": 460, "departure": "09:00", "on_time": "88%"}, {"number": "MU5234", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "nonstop", "fare": 580, "departure": "07:30", "on_time": "91%"}, {"number": "CZ3401", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-22", "airline": "China Southern", "fare": 320, "taxes": 70}]}
      - city directory: {"Chengdu": {"code": "CTU", "group": "Popular"}, "Guangzhou": {"code": "CAN", "group": "GHIJ"}}
    - **When:** Choose Departure date 2026-07-22, select Economy in Cabin class and click Update results.
    - **Then:** Flight results remains open with July 22 and Economy retained, and Flight list contains only CZ3401 priced ¥320.
    - **References:** `\ref[requirement](REQ-2.4)`, `\ref[requirement](REQ-2.5)`, `\ref[image](IMG-SEARCH-PANEL)`

### REQ-2.7 Filter flights by stops and airline

Selecting "Nonstop only"(role=checkbox) removes JD5162 from "Flight list"(role=region). Selecting China Southern in "Airline"(role=combobox) additionally leaves only CZ3401; the filters compose without resetting each other.

Time and airport filters remain capability context without specified detailed behavior.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

Dates and time-dependent behavior use Asia/Shanghai and the shared application/evaluator time 2026-07-19T08:00:00+08:00; public countdowns use elapsed time.

Published flight identity includes route, date and dataset. Flight identity includes origin, destination, date and flight number.

**IMG-SEARCH-RESULTS · flight_results**

![IMG-SEARCH-RESULTS · flight_results](reference/search_results.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.4

**Scenarios:**

- SCN-REQ-2.7-01 — Compose nonstop and airline filters
  - **Step:** STEP-REQ-2.7-01-01
    - **Given:** The visitor has used Origin Chengdu, Destination Guangzhou, Departure date 2026-07-21 and Search flights; Flight list contains CZ3401 (¥320, 11:00, 95%, nonstop), JD5162 (¥460, 09:00, 88%, stopover) and MU5234 (¥580, 07:30, 91%, nonstop).
      Seed prerequisites (prepared before this scenario):
      - published booking inventory: {"flights": [{"number": "CZ3401", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "China Southern", "stops": "nonstop", "fare": 320, "departure": "11:00", "on_time": "95%"}, {"number": "JD5162", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "stopover", "fare": 460, "departure": "09:00", "on_time": "88%"}, {"number": "MU5234", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "nonstop", "fare": 580, "departure": "07:30", "on_time": "91%"}]}
      - city directory: {"Chengdu": {"code": "CTU", "group": "Popular"}, "Guangzhou": {"code": "CAN", "group": "GHIJ"}}
    - **When:** Check Nonstop only, inspect the results, then select China Southern in Airline.
    - **Then:** Nonstop first leaves CZ3401 and MU5234 and excludes JD5162; adding the airline filter leaves only CZ3401.
    - **References:** `\ref[requirement](REQ-2.4)`, `\ref[image](IMG-SEARCH-RESULTS)`

### REQ-2.8 Sort matching flights

"Price: low to high"(role=button), "On-time: high to low"(role=button), and "Departure: earliest first"(role=button) order "Flight list"(role=region) by numeric fare, numeric on-time rate, or chronological departure respectively. Sorting preserves flight identities, whose accessible sequence makes order observable without using position to choose a business record.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

Dates and time-dependent behavior use Asia/Shanghai and the shared application/evaluator time 2026-07-19T08:00:00+08:00; public countdowns use elapsed time.

Published flight identity includes route, date and dataset. Flight identity includes origin, destination, date and flight number.

**IMG-SEARCH-RESULTS · flight_results**

![IMG-SEARCH-RESULTS · flight_results](reference/search_results.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.4

**Scenarios:**

- SCN-REQ-2.8-01 — Order by lowest price
  - **Step:** STEP-REQ-2.8-01-01
    - **Given:** The visitor has used Origin Chengdu, Destination Guangzhou, Departure date 2026-07-21 and Search flights; Flight list contains CZ3401 (¥320, 11:00, 95%, nonstop), JD5162 (¥460, 09:00, 88%, stopover) and MU5234 (¥580, 07:30, 91%, nonstop).
      Seed prerequisites (prepared before this scenario):
      - published booking inventory: {"flights": [{"number": "CZ3401", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "China Southern", "stops": "nonstop", "fare": 320, "departure": "11:00", "on_time": "95%"}, {"number": "JD5162", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "stopover", "fare": 460, "departure": "09:00", "on_time": "88%"}, {"number": "MU5234", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "nonstop", "fare": 580, "departure": "07:30", "on_time": "91%"}]}
      - city directory: {"Chengdu": {"code": "CTU", "group": "Popular"}, "Guangzhou": {"code": "CAN", "group": "GHIJ"}}
    - **When:** Click Price: low to high.
    - **Then:** The three flights remain and their visible order is CZ3401, JD5162, MU5234.
    - **References:** `\ref[requirement](REQ-2.4)`, `\ref[image](IMG-SEARCH-RESULTS)`
- SCN-REQ-2.8-02 — Order by highest punctuality
  - **Step:** STEP-REQ-2.8-02-01
    - **Given:** The visitor has used Origin Chengdu, Destination Guangzhou, Departure date 2026-07-21 and Search flights; Flight list contains CZ3401 (¥320, 11:00, 95%, nonstop), JD5162 (¥460, 09:00, 88%, stopover) and MU5234 (¥580, 07:30, 91%, nonstop).
      Seed prerequisites (prepared before this scenario):
      - published booking inventory: {"flights": [{"number": "CZ3401", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "China Southern", "stops": "nonstop", "fare": 320, "departure": "11:00", "on_time": "95%"}, {"number": "JD5162", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "stopover", "fare": 460, "departure": "09:00", "on_time": "88%"}, {"number": "MU5234", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "nonstop", "fare": 580, "departure": "07:30", "on_time": "91%"}]}
      - city directory: {"Chengdu": {"code": "CTU", "group": "Popular"}, "Guangzhou": {"code": "CAN", "group": "GHIJ"}}
    - **When:** Click On-time: high to low.
    - **Then:** The three flights remain and their visible order is CZ3401, MU5234, JD5162.
    - **References:** `\ref[requirement](REQ-2.4)`, `\ref[image](IMG-SEARCH-RESULTS)`
- SCN-REQ-2.8-03 — Order by earliest departure
  - **Step:** STEP-REQ-2.8-03-01
    - **Given:** The visitor has used Origin Chengdu, Destination Guangzhou, Departure date 2026-07-21 and Search flights; Flight list contains CZ3401 (¥320, 11:00, 95%, nonstop), JD5162 (¥460, 09:00, 88%, stopover) and MU5234 (¥580, 07:30, 91%, nonstop).
      Seed prerequisites (prepared before this scenario):
      - published booking inventory: {"flights": [{"number": "CZ3401", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "China Southern", "stops": "nonstop", "fare": 320, "departure": "11:00", "on_time": "95%"}, {"number": "JD5162", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "stopover", "fare": 460, "departure": "09:00", "on_time": "88%"}, {"number": "MU5234", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "nonstop", "fare": 580, "departure": "07:30", "on_time": "91%"}]}
      - city directory: {"Chengdu": {"code": "CTU", "group": "Popular"}, "Guangzhou": {"code": "CAN", "group": "GHIJ"}}
    - **When:** Click Departure: earliest first.
    - **Then:** The three flights remain and their visible order is MU5234, JD5162, CZ3401.
    - **References:** `\ref[requirement](REQ-2.4)`, `\ref[image](IMG-SEARCH-RESULTS)`

### REQ-2.9 Inspect and collapse fare options

Within "Flight JD5162"(role=listitem), Show fares reveals Fare options with its Economy fare group and Refund and change rules. Hide fares closes those options and restores Show fares.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

Dates and time-dependent behavior use Asia/Shanghai and the shared application/evaluator time 2026-07-19T08:00:00+08:00; public countdowns use elapsed time.

Published flight identity includes route, date and dataset. Flight identity includes origin, destination, date and flight number.

**IMG-SEARCH-RESULTS · flight_results**

![IMG-SEARCH-RESULTS · flight_results](reference/search_results.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.4

**Scenarios:**

- SCN-REQ-2.9-01 — Expand and collapse the selected flight fare
  - **Step:** STEP-REQ-2.9-01-01
    - **Given:** The visitor has used Origin Chengdu, Destination Guangzhou, Departure date 2026-07-21 and Search flights; Flight list contains CZ3401 (¥320, 11:00, 95%, nonstop), JD5162 (¥460, 09:00, 88%, stopover) and MU5234 (¥580, 07:30, 91%, nonstop).
      Seed prerequisites (prepared before this scenario):
      - published booking inventory: {"flights": [{"number": "CZ3401", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "China Southern", "stops": "nonstop", "fare": 320, "departure": "11:00", "on_time": "95%"}, {"number": "JD5162", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "stopover", "fare": 460, "departure": "09:00", "on_time": "88%"}, {"number": "MU5234", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "nonstop", "fare": 580, "departure": "07:30", "on_time": "91%"}]}
      - city directory: {"Chengdu": {"code": "CTU", "group": "Popular"}, "Guangzhou": {"code": "CAN", "group": "GHIJ"}}
    - **When:** Click Show fares within Flight JD5162, inspect its Fare options, then click Hide fares within the same flight.
    - **Then:** Fare options displays Economy fare and Refund and change rules; Hide fares closes that region and restores Show fares.
    - **References:** `\ref[requirement](REQ-2.4)`, `\ref[image](IMG-SEARCH-RESULTS)`

### REQ-2.10 Select the identified flight and fare

Within "Flight JD5162"(role=listitem), "Show fares"(role=button) exposes "Economy fare"(role=group). Clicking its "Book"(role=button) opens Book flight for JD5162 with the selected route, date, and fare preserved. Signed-out booking is allowed.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

Dates and time-dependent behavior use Asia/Shanghai and the shared application/evaluator time 2026-07-19T08:00:00+08:00; public countdowns use elapsed time.

Published flight identity includes route, date and dataset. Flight identity includes origin, destination, date and flight number.

**IMG-SEARCH-RESULTS · flight_results**

![IMG-SEARCH-RESULTS · flight_results](reference/search_results.png)

**IMG-BOOK2 · booking**

![IMG-BOOK2 · booking](reference/book2.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.9

**Scenarios:**

- SCN-REQ-2.10-01 — Book JD5162 Economy fare
  - **Step:** STEP-REQ-2.10-01-01
    - **Given:** The visitor has used Origin Chengdu, Destination Guangzhou, Departure date 2026-07-21 and Search flights; Flight list contains CZ3401 (¥320, 11:00, 95%, nonstop), JD5162 (¥460, 09:00, 88%, stopover) and MU5234 (¥580, 07:30, 91%, nonstop). The visitor remains anonymous.
      Seed prerequisites (prepared before this scenario):
      - published booking inventory: {"flights": [{"number": "CZ3401", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "China Southern", "stops": "nonstop", "fare": 320, "departure": "11:00", "on_time": "95%"}, {"number": "JD5162", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "stopover", "fare": 460, "departure": "09:00", "on_time": "88%"}, {"number": "MU5234", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "nonstop", "fare": 580, "departure": "07:30", "on_time": "91%"}], "jd5162": {"taxes_per_passenger": 70, "baggage_kg": 20, "refund_fee": 100}}
      - city directory: {"Chengdu": {"code": "CTU", "group": "Popular"}, "Guangzhou": {"code": "CAN", "group": "GHIJ"}}
    - **When:** Click Show fares within Flight JD5162 and Book within its Economy fare group.
    - **Then:** Book flight opens for JD5162 with the selected Chengdu–Guangzhou route, July 21 and Economy fare retained.
    - **References:** `\ref[requirement](REQ-2.9)`, `\ref[image](IMG-SEARCH-RESULTS)`, `\ref[image](IMG-BOOK2)`

### REQ-2.11 Change route criteria on flight results

Users can edit "Origin"(role=textbox), "Destination"(role=textbox), and "Departure date"(role=textbox) on results. "Update results"(role=button) queries the changed route rather than retaining old flights; Beihai–Mars City on July 23 shows the defined empty "Flight list"(role=region) with updated criteria.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

Dates and time-dependent behavior use Asia/Shanghai and the shared application/evaluator time 2026-07-19T08:00:00+08:00; public countdowns use elapsed time.

Published flight identity includes route, date and dataset. Flight identity includes origin, destination, date and flight number.

**IMG-SEARCH-PANEL · flight_results**

![IMG-SEARCH-PANEL · flight_results](reference/search_panel.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.6

**Scenarios:**

- SCN-REQ-2.11-01 — Change route criteria on flight results
  - **Step:** STEP-REQ-2.11-01-01
    - **Given:** The visitor has used Origin Chengdu, Destination Guangzhou, Departure date 2026-07-21 and Search flights; Flight list contains CZ3401 (¥320, 11:00, 95%, nonstop), JD5162 (¥460, 09:00, 88%, stopover) and MU5234 (¥580, 07:30, 91%, nonstop).
      Seed prerequisites (prepared before this scenario):
      - published booking inventory: {"flights": [{"number": "CZ3401", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "China Southern", "stops": "nonstop", "fare": 320, "departure": "11:00", "on_time": "95%"}, {"number": "JD5162", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "stopover", "fare": 460, "departure": "09:00", "on_time": "88%"}, {"number": "MU5234", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "nonstop", "fare": 580, "departure": "07:30", "on_time": "91%"}]}
      - city directory: {"Chengdu": {"code": "CTU", "group": "Popular"}, "Guangzhou": {"code": "CAN", "group": "GHIJ"}}
    - **When:** Replace Origin with Beihai and Destination with Mars City, choose Departure date 2026-07-23 and click Update results.
    - **Then:** Flight results retains the changed criteria; Flight list contains no flights and displays No flights found and Modify search instead of the old route results.
    - **References:** `\ref[requirement](REQ-2.6)`, `\ref[image](IMG-SEARCH-PANEL)`

### REQ-2.12 Recover from an empty flight search

Modify search from an empty "Flight list"(role=region) reveals editable "Origin"(role=textbox) and "Destination"(role=textbox) criteria, either inline or in quick search. Correcting the route and date and using "Search flights"(role=button) or "Update results"(role=button), as appropriate to the current form, restores published matches. The form's location is unrestricted.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

Dates and time-dependent behavior use Asia/Shanghai and the shared application/evaluator time 2026-07-19T08:00:00+08:00; public countdowns use elapsed time.

Published flight identity includes route, date and dataset. Flight identity includes origin, destination, date and flight number.

**IMG-SEARCH-RESULTS · flight_results**

![IMG-SEARCH-RESULTS · flight_results](reference/search_results.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.4

**Scenarios:**

- SCN-REQ-2.12-01 — Recover from an empty flight search
  - **Step:** STEP-REQ-2.12-01-01
    - **Given:** The visitor has searched Beihai–Mars City for July 23 and Flight list displays No flights found.
      Seed prerequisites (prepared before this scenario):
      - published booking inventory: {"flights": [{"number": "CZ3401", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "China Southern", "stops": "nonstop", "fare": 320, "departure": "11:00", "on_time": "95%"}, {"number": "JD5162", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "stopover", "fare": 460, "departure": "09:00", "on_time": "88%"}, {"number": "MU5234", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "nonstop", "fare": 580, "departure": "07:30", "on_time": "91%"}], "empty_query": {"origin": "Beihai", "destination": "Mars City", "date": "2026-07-23"}}
      - city directory: {"Chengdu": {"code": "CTU", "group": "Popular"}, "Guangzhou": {"code": "CAN", "group": "GHIJ"}}
    - **When:** Click Modify search, fill Origin Chengdu and Destination Guangzhou, choose July 21 and submit the exposed Search flights or Update results action.
    - **Then:** Flight results displays exactly CZ3401, JD5162 and MU5234 for the corrected route.
    - **References:** `\ref[requirement](REQ-2.4)`, `\ref[image](IMG-SEARCH-RESULTS)`

### REQ-2.13 Restore flights after removing nonstop filter

With "Origin"(role=textbox), "Destination"(role=textbox), and "Departure date"(role=textbox) retained, clearing "Nonstop only"(role=checkbox) restores matching stopover flights to "Flight list"(role=region), preserving unchanged filters.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

Dates and time-dependent behavior use Asia/Shanghai and the shared application/evaluator time 2026-07-19T08:00:00+08:00; public countdowns use elapsed time.

Published flight identity includes route, date and dataset. Flight identity includes origin, destination, date and flight number.

**IMG-SEARCH-RESULTS · flight_results**

![IMG-SEARCH-RESULTS · flight_results](reference/search_results.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.7

**Scenarios:**

- SCN-REQ-2.13-01 — Restore flights after removing nonstop filter
  - **Step:** STEP-REQ-2.13-01-01
    - **Given:** The visitor has used Origin Chengdu, Destination Guangzhou, Departure date 2026-07-21 and Search flights; Flight list contains CZ3401 (¥320, 11:00, 95%, nonstop), JD5162 (¥460, 09:00, 88%, stopover) and MU5234 (¥580, 07:30, 91%, nonstop).
      Seed prerequisites (prepared before this scenario):
      - published booking inventory: {"flights": [{"number": "CZ3401", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "China Southern", "stops": "nonstop", "fare": 320, "departure": "11:00", "on_time": "95%"}, {"number": "JD5162", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "stopover", "fare": 460, "departure": "09:00", "on_time": "88%"}, {"number": "MU5234", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "nonstop", "fare": 580, "departure": "07:30", "on_time": "91%"}]}
      - city directory: {"Chengdu": {"code": "CTU", "group": "Popular"}, "Guangzhou": {"code": "CAN", "group": "GHIJ"}}
    - **When:** Check Nonstop only, verify two results, then uncheck it.
    - **Then:** CZ3401, JD5162 and MU5234 all return; Origin Chengdu, Destination Guangzhou and July 21 remain unchanged.
    - **References:** `\ref[requirement](REQ-2.7)`, `\ref[image](IMG-SEARCH-RESULTS)`

### REQ-2.14 Remove airline filter while keeping nonstop preference

"Airline"(role=combobox) offers All airlines. With China Southern and "Nonstop only"(role=checkbox) selected, choosing All airlines removes only the airline restriction and restores MU5234 to "Flight list"(role=region), while stopover JD5162 remains excluded.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

Dates and time-dependent behavior use Asia/Shanghai and the shared application/evaluator time 2026-07-19T08:00:00+08:00; public countdowns use elapsed time.

Published flight identity includes route, date and dataset. Flight identity includes origin, destination, date and flight number.

**IMG-SEARCH-RESULTS · flight_results**

![IMG-SEARCH-RESULTS · flight_results](reference/search_results.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.7

**Scenarios:**

- SCN-REQ-2.14-01 — Remove airline filter while keeping nonstop preference
  - **Step:** STEP-REQ-2.14-01-01
    - **Given:** The visitor has used Origin Chengdu, Destination Guangzhou, Departure date 2026-07-21 and Search flights; Flight list contains CZ3401 (¥320, 11:00, 95%, nonstop), JD5162 (¥460, 09:00, 88%, stopover) and MU5234 (¥580, 07:30, 91%, nonstop).
      Seed prerequisites (prepared before this scenario):
      - published booking inventory: {"flights": [{"number": "CZ3401", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "China Southern", "stops": "nonstop", "fare": 320, "departure": "11:00", "on_time": "95%"}, {"number": "JD5162", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "stopover", "fare": 460, "departure": "09:00", "on_time": "88%"}, {"number": "MU5234", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "nonstop", "fare": 580, "departure": "07:30", "on_time": "91%"}]}
      - city directory: {"Chengdu": {"code": "CTU", "group": "Popular"}, "Guangzhou": {"code": "CAN", "group": "GHIJ"}}
    - **When:** Check Nonstop only and select China Southern, verify only CZ3401 remains, then select All airlines.
    - **Then:** Nonstop only stays checked; CZ3401 and MU5234 are displayed while stopover JD5162 remains excluded.
    - **References:** `\ref[requirement](REQ-2.7)`, `\ref[image](IMG-SEARCH-RESULTS)`

## REQ-3 Book, price and pay for flights

Support select frequent passengers and recalculate totals, validate ad hoc passenger identity, confirm booking contact mobile, submit passenger booking to cashier, pay a submitted order, remove one selected frequent passenger, reject order submission with an invalid passenger ID, require booking terms before order submission.

**Type:** FOLDER
**Dependencies:** None

### REQ-3.1 Select frequent passengers and recalculate totals

Signed-in users choose Zhang San and Li Si using the "Zhang San"(role=checkbox) and "Li Si"(role=checkbox) choices within "Frequent passengers"(role=region). Their identities appear in "Selected passengers"(role=region), and "Fee breakdown"(role=region) updates from Passengers: 1 and Order total: ¥530 to Passengers: 2 and Order total: ¥1060, using ¥460 fare plus ¥70 tax per passenger.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

The verified ctrip_user account initially has frequent passengers Zhang San and Li Si; they are retained seed records because The application does not expose personal traveler maintenance. Selecting these existing travelers is required; creating them in a personal center is not required.

**IMG-BOOK2 · booking**

![IMG-BOOK2 · booking](reference/book2.png)

**Type:** ATOMIC
**Dependencies:** REQ-1.3, REQ-2.10

**Scenarios:**

- SCN-REQ-3.1-01 — Fill two passengers with corresponding total
  - **Step:** STEP-REQ-3.1-01-01
    - **Given:** The visitor has searched Chengdu–Guangzhou for July 21, clicked Show fares in Flight JD5162 and Book in Economy fare; Book flight is open with one-passenger fare ¥460 plus tax ¥70, total ¥530. The verified user is signed in and has seeded frequent travelers Zhang San and Li Si; Fee breakdown initially shows Passengers: 1 and ¥530.
      Seed prerequisites (prepared before this scenario):
      - existing verified accounts: {"user": {"email": "ctrip_user@example.com", "password": "Travel1234", "username": "ctrip_user", "mobile": "13800000010"}}
      - published booking inventory: {"flights": [{"number": "CZ3401", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "China Southern", "stops": "nonstop", "fare": 320, "departure": "11:00", "on_time": "95%"}, {"number": "JD5162", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "stopover", "fare": 460, "departure": "09:00", "on_time": "88%"}, {"number": "MU5234", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "nonstop", "fare": 580, "departure": "07:30", "on_time": "91%"}], "jd5162": {"taxes_per_passenger": 70, "baggage_kg": 20, "refund_fee": 100}}
      - city directory: {"Chengdu": {"code": "CTU", "group": "Popular"}, "Guangzhou": {"code": "CAN", "group": "GHIJ"}}
      - immutable legacy personal records: {"user": {"travelers": [{"name": "Zhang San"}, {"name": "Li Si"}]}}
    - **When:** Check Zhang San and Li Si within Frequent passengers.
    - **Then:** Selected passengers contains exactly those two named records; Fee breakdown shows Passengers: 2 and Order total: ¥1060.
    - **References:** `\ref[requirement](REQ-2.10)`, `\ref[requirement](REQ-1.3)`, `\ref[image](IMG-BOOK2)`

### REQ-3.2 Validate ad hoc passenger identity

"Passenger details"(role=region) provides Full name and ID number for an ad hoc passenger, alongside "Contact mobile"(role=textbox). Leaving ID number validates its checksum: the source valid ID is accepted, while 123 shows Enter a valid ID number. The passenger is not saved as a frequent traveler, and no civil-identity separate data-definition lookup is required.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

**IMG-BOOK2 · booking**

![IMG-BOOK2 · booking](reference/book2.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.10

**Scenarios:**

- SCN-REQ-3.2-01 — Accept checksum-valid passenger identity
  - **Step:** STEP-REQ-3.2-01-01
    - **Given:** The visitor has searched Chengdu–Guangzhou for July 21, clicked Show fares in Flight JD5162 and Book in Economy fare; Book flight is open with one-passenger fare ¥460 plus tax ¥70, total ¥530.
      Seed prerequisites (prepared before this scenario):
      - published booking inventory: {"flights": [{"number": "CZ3401", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "China Southern", "stops": "nonstop", "fare": 320, "departure": "11:00", "on_time": "95%"}, {"number": "JD5162", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "stopover", "fare": 460, "departure": "09:00", "on_time": "88%"}, {"number": "MU5234", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "nonstop", "fare": 580, "departure": "07:30", "on_time": "91%"}], "jd5162": {"taxes_per_passenger": 70, "baggage_kg": 20, "refund_fee": 100}}
      - city directory: {"Chengdu": {"code": "CTU", "group": "Popular"}, "Guangzhou": {"code": "CAN", "group": "GHIJ"}}
    - **When:** Enter Full name Wang Wu and ID number 110101199001011237 in Passenger details, then focus Contact mobile to leave the ID field.
    - **Then:** The valid ID value remains and Passenger details has no visible validation alert.
    - **References:** `\ref[requirement](REQ-2.10)`, `\ref[image](IMG-BOOK2)`
- SCN-REQ-3.2-02 — Reject invalid passenger identity
  - **Step:** STEP-REQ-3.2-02-01
    - **Given:** The visitor has searched Chengdu–Guangzhou for July 21, clicked Show fares in Flight JD5162 and Book in Economy fare; Book flight is open with one-passenger fare ¥460 plus tax ¥70, total ¥530.
      Seed prerequisites (prepared before this scenario):
      - published booking inventory: {"flights": [{"number": "CZ3401", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "China Southern", "stops": "nonstop", "fare": 320, "departure": "11:00", "on_time": "95%"}, {"number": "JD5162", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "stopover", "fare": 460, "departure": "09:00", "on_time": "88%"}, {"number": "MU5234", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "nonstop", "fare": 580, "departure": "07:30", "on_time": "91%"}], "jd5162": {"taxes_per_passenger": 70, "baggage_kg": 20, "refund_fee": 100}}
      - city directory: {"Chengdu": {"code": "CTU", "group": "Popular"}, "Guangzhou": {"code": "CAN", "group": "GHIJ"}}
    - **When:** Enter Full name Wang Wu and ID number 123 in Passenger details, then focus Contact mobile.
    - **Then:** Passenger details displays Enter a valid ID number.
    - **References:** `\ref[requirement](REQ-2.10)`, `\ref[image](IMG-BOOK2)`

### REQ-3.3 Confirm booking contact mobile

"Contact mobile"(role=textbox) defaults to the signed-in mobile 13800000010. Replacing it with valid 13800000014 and leaving focus retains the value without a contact validation alert in "Contact information"(role=region). Contact feedback remains separate from "Passenger details"(role=region).

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

Contact information is the named booking contact-validation region.

**IMG-BOOK2 · booking**

![IMG-BOOK2 · booking](reference/book2.png)

**Type:** ATOMIC
**Dependencies:** REQ-1.3, REQ-2.10

**Scenarios:**

- SCN-REQ-3.3-01 — Replace prefilled contact mobile
  - **Step:** STEP-REQ-3.3-01-01
    - **Given:** The visitor has searched Chengdu–Guangzhou for July 21, clicked Show fares in Flight JD5162 and Book in Economy fare; Book flight is open with one-passenger fare ¥460 plus tax ¥70, total ¥530. The verified user is signed in and Contact mobile initially shows 13800000010.
      Seed prerequisites (prepared before this scenario):
      - existing verified accounts: {"user": {"email": "ctrip_user@example.com", "password": "Travel1234", "username": "ctrip_user", "mobile": "13800000010"}}
      - published booking inventory: {"flights": [{"number": "CZ3401", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "China Southern", "stops": "nonstop", "fare": 320, "departure": "11:00", "on_time": "95%"}, {"number": "JD5162", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "stopover", "fare": 460, "departure": "09:00", "on_time": "88%"}, {"number": "MU5234", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "nonstop", "fare": 580, "departure": "07:30", "on_time": "91%"}], "jd5162": {"taxes_per_passenger": 70, "baggage_kg": 20, "refund_fee": 100}}
      - city directory: {"Chengdu": {"code": "CTU", "group": "Popular"}, "Guangzhou": {"code": "CAN", "group": "GHIJ"}}
    - **When:** Replace Contact mobile with 13800000014, then focus Full name in Passenger details.
    - **Then:** The replacement mobile remains and Contact information has no visible validation alert.
    - **References:** `\ref[requirement](REQ-2.10)`, `\ref[requirement](REQ-1.3)`, `\ref[image](IMG-BOOK2)`

### REQ-3.4 Submit passenger booking to cashier

A guest completes "Full name"(role=textbox) and "ID number"(role=textbox) in "Passenger details"(role=region) with Wang Wu and checksum-valid 110101199001011237, enters 13800000014 in "Contact mobile"(role=textbox), selects "Agree to booking terms"(role=checkbox), and clicks "Submit order"(role=button). The JD5162 order awaits payment, showing Payment heading, "Time remaining"(role=timer) with textual remaining duration, and Unpaid orders are cancelled when the timer expires.

Public countdowns use "Time remaining"(role=timer) and render MM:SS or HH:MM:SS.

For new flight orders: Created by Submit order; paid only using simulated Alipay.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

Dates and time-dependent behavior use Asia/Shanghai and the shared application/evaluator time 2026-07-19T08:00:00+08:00; public countdowns use elapsed time.

Payment is simulated. Public countdowns are named Time remaining and display MM:SS or HH:MM:SS.

**IMG-BOOK2 · booking**

![IMG-BOOK2 · booking](reference/book2.png)

**IMG-BOOK4 · payment**

![IMG-BOOK4 · payment](reference/book4.png)

**Type:** ATOMIC
**Dependencies:** REQ-3.2, REQ-3.3

**Scenarios:**

- SCN-REQ-3.4-01 — Submit a valid unpaid booking
  - **Step:** STEP-REQ-3.4-01-01
    - **Given:** The visitor has searched Chengdu–Guangzhou for July 21, clicked Show fares in Flight JD5162 and Book in Economy fare; Book flight is open with one-passenger fare ¥460 plus tax ¥70, total ¥530. The visitor is anonymous.
      Seed prerequisites (prepared before this scenario):
      - published booking inventory: {"flights": [{"number": "CZ3401", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "China Southern", "stops": "nonstop", "fare": 320, "departure": "11:00", "on_time": "95%"}, {"number": "JD5162", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "stopover", "fare": 460, "departure": "09:00", "on_time": "88%"}, {"number": "MU5234", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "nonstop", "fare": 580, "departure": "07:30", "on_time": "91%"}], "jd5162": {"taxes_per_passenger": 70, "baggage_kg": 20, "refund_fee": 100}}
      - city directory: {"Chengdu": {"code": "CTU", "group": "Popular"}, "Guangzhou": {"code": "CAN", "group": "GHIJ"}}
      - accepted test identity inputs: {"ids": ["110101199001011237"]}
    - **When:** Enter Full name Wang Wu and ID number 110101199001011237 in Passenger details, enter Contact mobile 13800000014, check Agree to booking terms and click Submit order.
    - **Then:** Payment opens with a visible Time remaining timer representing a positive duration and Unpaid orders are cancelled when the timer expires reminder.
    - **References:** `\ref[requirement](REQ-3.2)`, `\ref[image](IMG-BOOK2)`, `\ref[image](IMG-BOOK4)`

### REQ-3.5 Pay a submitted order

At the cashier, selecting "Alipay"(role=radio) and clicking "Pay now"(role=button) simulates payment for the submitted JD5162 order and displays Payment successful for that same order.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

Dates and time-dependent behavior use Asia/Shanghai and the shared application/evaluator time 2026-07-19T08:00:00+08:00; public countdowns use elapsed time.

Payment is simulated. Public countdowns are named Time remaining and display MM:SS or HH:MM:SS.

**IMG-BOOK4 · payment**

![IMG-BOOK4 · payment](reference/book4.png)

**Type:** ATOMIC
**Dependencies:** REQ-3.4

**Scenarios:**

- SCN-REQ-3.5-01 — Pay with simulated Alipay
  - **Step:** STEP-REQ-3.5-01-01
    - **Given:** The visitor has searched Chengdu–Guangzhou for July 21, clicked Show fares in Flight JD5162 and Book in Economy fare; Book flight is open with one-passenger fare ¥460 plus tax ¥70, total ¥530. Enter Full name Wang Wu and ID number 110101199001011237 in Passenger details, enter Contact mobile 13800000014, check Agree to booking terms and click Submit order. The resulting unpaid order is open at Payment.
      Seed prerequisites (prepared before this scenario):
      - published booking inventory: {"flights": [{"number": "CZ3401", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "China Southern", "stops": "nonstop", "fare": 320, "departure": "11:00", "on_time": "95%"}, {"number": "JD5162", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "stopover", "fare": 460, "departure": "09:00", "on_time": "88%"}, {"number": "MU5234", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "nonstop", "fare": 580, "departure": "07:30", "on_time": "91%"}], "jd5162": {"taxes_per_passenger": 70, "baggage_kg": 20, "refund_fee": 100}}
      - city directory: {"Chengdu": {"code": "CTU", "group": "Popular"}, "Guangzhou": {"code": "CAN", "group": "GHIJ"}}
      - accepted test identity inputs: {"ids": ["110101199001011237"]}
    - **When:** Select Alipay (radio) and click Pay now.
    - **Then:** Payment successful status appears and JD5162 remains visible for the same order.
    - **References:** `\ref[requirement](REQ-3.4)`, `\ref[image](IMG-BOOK4)`

### REQ-3.6 Remove one selected frequent passenger

Within "Frequent passengers"(role=region), deselecting Li Si after selecting both Zhang San and Li Si removes only Li Si from "Selected passengers"(role=region). "Fee breakdown"(role=region) returns to one passenger at ¥530.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

**IMG-BOOK2 · booking**

![IMG-BOOK2 · booking](reference/book2.png)

**Type:** ATOMIC
**Dependencies:** REQ-3.1

**Scenarios:**

- SCN-REQ-3.6-01 — Remove one selected frequent passenger
  - **Step:** STEP-REQ-3.6-01-01
    - **Given:** The visitor has searched Chengdu–Guangzhou for July 21, clicked Show fares in Flight JD5162 and Book in Economy fare; Book flight is open with one-passenger fare ¥460 plus tax ¥70, total ¥530. The signed-in user has checked Zhang San and Li Si through Frequent passengers, producing total ¥1060.
      Seed prerequisites (prepared before this scenario):
      - existing verified accounts: {"user": {"email": "ctrip_user@example.com", "password": "Travel1234", "username": "ctrip_user", "mobile": "13800000010"}}
      - published booking inventory: {"flights": [{"number": "CZ3401", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "China Southern", "stops": "nonstop", "fare": 320, "departure": "11:00", "on_time": "95%"}, {"number": "JD5162", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "stopover", "fare": 460, "departure": "09:00", "on_time": "88%"}, {"number": "MU5234", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "nonstop", "fare": 580, "departure": "07:30", "on_time": "91%"}], "jd5162": {"taxes_per_passenger": 70, "baggage_kg": 20, "refund_fee": 100}}
      - city directory: {"Chengdu": {"code": "CTU", "group": "Popular"}, "Guangzhou": {"code": "CAN", "group": "GHIJ"}}
      - immutable legacy personal records: {"user": {"travelers": [{"name": "Zhang San"}, {"name": "Li Si"}]}}
    - **When:** Uncheck Li Si within Frequent passengers.
    - **Then:** Selected passengers retains exactly Zhang San and excludes Li Si; Fee breakdown shows Passengers: 1 and total ¥530.
    - **References:** `\ref[requirement](REQ-3.1)`, `\ref[image](IMG-BOOK2)`

### REQ-3.7 Reject order submission with an invalid passenger ID

ID 123 in "Passenger details"(role=region) prevents "Submit order"(role=button) from creating a payable order even with valid "Contact mobile"(role=textbox) and selected "Agree to booking terms"(role=checkbox). Enter a valid ID number remains visible; Book flight stays open and Payment does not appear.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

**IMG-BOOK2 · booking**

![IMG-BOOK2 · booking](reference/book2.png)

**Type:** ATOMIC
**Dependencies:** REQ-3.2, REQ-3.4

**Scenarios:**

- SCN-REQ-3.7-01 — Reject order submission with an invalid passenger ID
  - **Step:** STEP-REQ-3.7-01-01
    - **Given:** The visitor has searched Chengdu–Guangzhou for July 21, clicked Show fares in Flight JD5162 and Book in Economy fare; Book flight is open with one-passenger fare ¥460 plus tax ¥70, total ¥530.
      Seed prerequisites (prepared before this scenario):
      - published booking inventory: {"flights": [{"number": "CZ3401", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "China Southern", "stops": "nonstop", "fare": 320, "departure": "11:00", "on_time": "95%"}, {"number": "JD5162", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "stopover", "fare": 460, "departure": "09:00", "on_time": "88%"}, {"number": "MU5234", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "nonstop", "fare": 580, "departure": "07:30", "on_time": "91%"}], "jd5162": {"taxes_per_passenger": 70, "baggage_kg": 20, "refund_fee": 100}}
      - city directory: {"Chengdu": {"code": "CTU", "group": "Popular"}, "Guangzhou": {"code": "CAN", "group": "GHIJ"}}
    - **When:** Enter Full name Wang Wu and ID number 123 in Passenger details, Contact mobile 13800000014 and checked Agree to booking terms, then click Submit order.
    - **Then:** Enter a valid ID number appears in Passenger details; Book flight remains and Payment is absent.
    - **References:** `\ref[requirement](REQ-3.2)`, `\ref[image](IMG-BOOK2)`

### REQ-3.8 Require booking terms before order submission

"Agree to booking terms"(role=checkbox) starts unchecked. Even with valid "Passenger details"(role=region) and "Contact mobile"(role=textbox), clicking "Submit order"(role=button) without agreement shows a visible validation alert, retains Book flight, and never advances to Payment. Alert wording is unrestricted.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

**IMG-BOOK2 · booking**

![IMG-BOOK2 · booking](reference/book2.png)

**Type:** ATOMIC
**Dependencies:** REQ-3.4

**Scenarios:**

- SCN-REQ-3.8-01 — Require booking terms before order submission
  - **Step:** STEP-REQ-3.8-01-01
    - **Given:** The visitor has searched Chengdu–Guangzhou for July 21, clicked Show fares in Flight JD5162 and Book in Economy fare; Book flight is open with one-passenger fare ¥460 plus tax ¥70, total ¥530. Agree to booking terms starts unchecked.
      Seed prerequisites (prepared before this scenario):
      - published booking inventory: {"flights": [{"number": "CZ3401", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "China Southern", "stops": "nonstop", "fare": 320, "departure": "11:00", "on_time": "95%"}, {"number": "JD5162", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "stopover", "fare": 460, "departure": "09:00", "on_time": "88%"}, {"number": "MU5234", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "nonstop", "fare": 580, "departure": "07:30", "on_time": "91%"}], "jd5162": {"taxes_per_passenger": 70, "baggage_kg": 20, "refund_fee": 100}}
      - city directory: {"Chengdu": {"code": "CTU", "group": "Popular"}, "Guangzhou": {"code": "CAN", "group": "GHIJ"}}
      - accepted test identity inputs: {"ids": ["110101199001011237"]}
    - **When:** Enter Wang Wu and valid ID 110101199001011237 in Passenger details and Contact mobile 13800000014, leave agreement unchecked and click Submit order.
    - **Then:** A visible validation alert appears; Book flight remains open and Payment is absent.
    - **References:** `\ref[requirement](REQ-3.2)`, `\ref[image](IMG-BOOK2)`

## REQ-4 Inspect and cancel orders

Support open account order list, search order by business number, inspect identified order details, cancel an unpaid order after confirmation, keep an unpaid order when cancellation is declined, keep order lists scoped to the current account.

**Type:** FOLDER
**Dependencies:** None

### REQ-4.1 Open account order list

"My account"(role=button) opens an account menu with Orders. Selecting Orders displays the heading and "Order list"(role=region), containing only orders owned by the signed-in account.

Order records are uniquely named "Record <order number>" within their list region, with actions scoped to that identity. Entries include order number, booking date, itinerary, flight, total, and display status. Not traveled and Pending review are distinct from payment state.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

Dates and time-dependent behavior use Asia/Shanghai and the shared application/evaluator time 2026-07-19T08:00:00+08:00; public countdowns use elapsed time.

Order entries are uniquely named Record <order number> within Order list, and row actions affect only that identity. Display lifecycle states Not traveled and Pending review are distinct from payment state.

Historical paid, completed and pending-review orders retain their stated historical dates independently of new booking submissions. Pending orders have a positive remaining timer and payment-expiry reminder; no exact expiry duration is specified.

The order list includes an All orders tab showing only the signed-in account's orders. Other lifecycle-tab filtering  is outside scope.

**IMG-ENTER-ORDER · home**

![IMG-ENTER-ORDER · home](reference/enter_order.png)

**IMG-ORDER1 · orders**

![IMG-ORDER1 · orders](reference/order1.png)

**Type:** ATOMIC
**Dependencies:** REQ-1.3

**Scenarios:**

- SCN-REQ-4.1-01 — Open orders from account menu
  - **Step:** STEP-REQ-4.1-01-01
    - **Given:** order_read has signed in through Log in with ctrip_order_read@example.com / Travel1234 and accepted terms.
      Seed prerequisites (prepared before this scenario):
      - existing verified accounts: {"order_read": {"email": "ctrip_order_read@example.com", "password": "Travel1234"}}
      - historical and cancellation orders: [{"owner": "order_read", "number": "CTRIP20260721001", "flight": "JD5162", "date": "2026-07-21", "origin": "Chengdu", "destination": "Guangzhou", "total": 530, "payment_status": "Pending payment", "display_status": "Pending payment"}, {"owner": "order_read", "number": "CTRIP20260722002", "flight": "CZ3401", "date": "2026-07-22", "total": 390, "payment_status": "Paid", "display_status": "Not traveled"}, {"owner": "order_read", "number": "CTRIP20260718003", "flight": "MU5234", "date": "2026-07-18", "total": 650, "payment_status": "Paid", "display_status": "Pending review"}]
    - **When:** Click My account, inspect the menu, then activate Orders.
    - **Then:** The menu contains Orders; Orders heading and Order list open for this account.
    - **References:** `\ref[requirement](REQ-1.3)`, `\ref[image](IMG-ENTER-ORDER)`, `\ref[image](IMG-ORDER1)`

### REQ-4.2 Search order by business number

Entering CTRIP20260721001 in "Order number"(role=textbox) and clicking "Search orders"(role=button) filters "Order list"(role=region) to that account-owned JD5162 order only.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

Dates and time-dependent behavior use Asia/Shanghai and the shared application/evaluator time 2026-07-19T08:00:00+08:00; public countdowns use elapsed time.

Order entries are uniquely named Record <order number> within Order list, and row actions affect only that identity. Display lifecycle states Not traveled and Pending review are distinct from payment state.

**IMG-ORDER1 · orders**

![IMG-ORDER1 · orders](reference/order1.png)

**Type:** ATOMIC
**Dependencies:** REQ-4.1

**Scenarios:**

- SCN-REQ-4.2-01 — Find exact order number
  - **Step:** STEP-REQ-4.2-01-01
    - **Given:** order_read has signed in using ctrip_order_read@example.com / Travel1234 and checked Agree to terms, then opened My account → Orders. Its seeded orders are CTRIP20260721001/JD5162/¥530/Pending payment, CTRIP20260722002/CZ3401/¥390/Not traveled and CTRIP20260718003/MU5234/¥650/Pending review.
      Seed prerequisites (prepared before this scenario):
      - existing verified accounts: {"order_read": {"email": "ctrip_order_read@example.com", "password": "Travel1234"}}
      - historical and cancellation orders: [{"owner": "order_read", "number": "CTRIP20260721001", "flight": "JD5162", "date": "2026-07-21", "origin": "Chengdu", "destination": "Guangzhou", "total": 530, "payment_status": "Pending payment", "display_status": "Pending payment"}, {"owner": "order_read", "number": "CTRIP20260722002", "flight": "CZ3401", "date": "2026-07-22", "total": 390, "payment_status": "Paid", "display_status": "Not traveled"}, {"owner": "order_read", "number": "CTRIP20260718003", "flight": "MU5234", "date": "2026-07-18", "total": 650, "payment_status": "Paid", "display_status": "Pending review"}]
    - **When:** Enter CTRIP20260721001 in Order number and click Search orders.
    - **Then:** Exactly that JD5162 record remains; CTRIP20260722002 and CTRIP20260718003 are excluded.
    - **References:** `\ref[requirement](REQ-4.1)`, `\ref[image](IMG-ORDER1)`

### REQ-4.3 Inspect identified order details

View details within CTRIP20260721001 opens its Order details with number, "Flight itinerary"(role=region) showing JD5162 and Chengdu–Guangzhou, and Refund and change rules. "Payment status"(role=region) displays Pending payment, a decreasing Time remaining timer, expiry reminder, Pay now, and Cancel order. Browser time may be advanced for countdown observation while server dates remain externally fixed.

Public countdowns use "Time remaining"(role=timer) and render MM:SS or HH:MM:SS.

Order-detail terminals, operating carrier, non-flight services, masked passengers, and fee summary remain source context without additional concrete fixtures or oracles.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

Dates and time-dependent behavior use Asia/Shanghai and the shared application/evaluator time 2026-07-19T08:00:00+08:00; public countdowns use elapsed time.

Order entries are uniquely named Record <order number> within Order list, and row actions affect only that identity. Display lifecycle states Not traveled and Pending review are distinct from payment state.

Historical paid, completed and pending-review orders retain their stated historical dates independently of new booking submissions. Pending orders have a positive remaining timer and payment-expiry reminder; no exact expiry duration is specified.

**IMG-ORDER1 · orders**

![IMG-ORDER1 · orders](reference/order1.png)

**IMG-ORDER2 · order_details**

![IMG-ORDER2 · order_details](reference/order2.png)

**Type:** ATOMIC
**Dependencies:** REQ-4.1

**Scenarios:**

- SCN-REQ-4.3-01 — Inspect unpaid itinerary and payment countdown
  - **Step:** STEP-REQ-4.3-01-01
    - **Given:** order_read has signed in using ctrip_order_read@example.com / Travel1234 and checked Agree to terms, then opened My account → Orders. Its seeded orders are CTRIP20260721001/JD5162/¥530/Pending payment, CTRIP20260722002/CZ3401/¥390/Not traveled and CTRIP20260718003/MU5234/¥650/Pending review. View details has been clicked within CTRIP20260721001.
      Seed prerequisites (prepared before this scenario):
      - existing verified accounts: {"order_read": {"email": "ctrip_order_read@example.com", "password": "Travel1234"}}
      - historical and cancellation orders: [{"owner": "order_read", "number": "CTRIP20260721001", "flight": "JD5162", "date": "2026-07-21", "origin": "Chengdu", "destination": "Guangzhou", "total": 530, "payment_status": "Pending payment", "display_status": "Pending payment"}, {"owner": "order_read", "number": "CTRIP20260722002", "flight": "CZ3401", "date": "2026-07-22", "total": 390, "payment_status": "Paid", "display_status": "Not traveled"}, {"owner": "order_read", "number": "CTRIP20260718003", "flight": "MU5234", "date": "2026-07-18", "total": 650, "payment_status": "Paid", "display_status": "Pending review"}]
    - **When:** Inspect Order details, Flight itinerary and Payment status; record Time remaining and advance browser elapsed time by 1.1 seconds.
    - **Then:** The order number, JD5162 and Chengdu to Guangzhou are visible; itinerary offers Refund and change rules; Payment status displays Pending payment, expiry reminder, Pay now and Cancel order, and its positive Time remaining decreases.
    - **References:** `\ref[requirement](REQ-4.1)`, `\ref[image](IMG-ORDER1)`, `\ref[image](IMG-ORDER2)`
- SCN-REQ-4.3-02 — Read refund and change conditions
  - **Step:** STEP-REQ-4.3-02-01
    - **Given:** order_read has signed in using ctrip_order_read@example.com / Travel1234 and checked Agree to terms, then opened My account → Orders. Its seeded orders are CTRIP20260721001/JD5162/¥530/Pending payment, CTRIP20260722002/CZ3401/¥390/Not traveled and CTRIP20260718003/MU5234/¥650/Pending review. View details has been clicked within CTRIP20260721001.
      Seed prerequisites (prepared before this scenario):
      - existing verified accounts: {"order_read": {"email": "ctrip_order_read@example.com", "password": "Travel1234"}}
      - published booking inventory: {"flights": [{"number": "CZ3401", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "China Southern", "stops": "nonstop", "fare": 320, "departure": "11:00", "on_time": "95%"}, {"number": "JD5162", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "stopover", "fare": 460, "departure": "09:00", "on_time": "88%"}, {"number": "MU5234", "origin": "Chengdu", "destination": "Guangzhou", "date": "2026-07-21", "airline": "Other airline", "stops": "nonstop", "fare": 580, "departure": "07:30", "on_time": "91%"}], "jd5162": {"taxes_per_passenger": 70, "baggage_kg": 20, "refund_fee": 100}}
      - historical and cancellation orders: [{"owner": "order_read", "number": "CTRIP20260721001", "flight": "JD5162", "date": "2026-07-21", "origin": "Chengdu", "destination": "Guangzhou", "total": 530, "payment_status": "Pending payment", "display_status": "Pending payment"}, {"owner": "order_read", "number": "CTRIP20260722002", "flight": "CZ3401", "date": "2026-07-22", "total": 390, "payment_status": "Paid", "display_status": "Not traveled"}, {"owner": "order_read", "number": "CTRIP20260718003", "flight": "MU5234", "date": "2026-07-18", "total": 650, "payment_status": "Paid", "display_status": "Pending review"}]
    - **When:** Click Refund and change rules within Flight itinerary.
    - **Then:** Flight itinerary displays Refund fee: ¥100 and Changes allowed before departure.
    - **References:** `\ref[requirement](REQ-4.1)`, `\ref[image](IMG-ORDER1)`, `\ref[image](IMG-ORDER2)`

### REQ-4.4 Cancel an unpaid order after confirmation

The independent order_cancel account owns CTRIP20260721004. Clicking "Cancel order"(role=button) in "Payment status"(role=region) opens "Cancel order"(role=dialog); Confirm cancellation changes that same order to Closed, persisting after reload.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

Dates and time-dependent behavior use Asia/Shanghai and the shared application/evaluator time 2026-07-19T08:00:00+08:00; public countdowns use elapsed time.

Order entries are uniquely named Record <order number> within Order list, and row actions affect only that identity. Display lifecycle states Not traveled and Pending review are distinct from payment state.

**IMG-ORDER2 · order_details**

![IMG-ORDER2 · order_details](reference/order2.png)

**IMG-ORDER1 · orders**

![IMG-ORDER1 · orders](reference/order1.png)

**Type:** ATOMIC
**Dependencies:** REQ-4.3

**Scenarios:**

- SCN-REQ-4.4-01 — Confirm unpaid order cancellation
  - **Step:** STEP-REQ-4.4-01-01
    - **Given:** order_cancel has signed in as ctrip_order_cancel@example.com / Travel1234 and opened Orders → CTRIP20260721004 → View details; Payment status is Pending payment.
      Seed prerequisites (prepared before this scenario):
      - existing verified accounts: {"order_cancel": {"email": "ctrip_order_cancel@example.com", "password": "Travel1234"}}
      - historical and cancellation orders: [{"owner": "order_cancel", "number": "CTRIP20260721004", "flight": "JD5162", "date": "2026-07-21", "total": 530, "payment_status": "Pending payment", "display_status": "Pending payment"}]
    - **When:** Click Cancel order within Payment status, then Confirm cancellation within Cancel order dialog; reload.
    - **Then:** The same CTRIP20260721004 displays Closed in Payment status before and after reload.
    - **References:** `\ref[requirement](REQ-4.3)`, `\ref[image](IMG-ORDER2)`, `\ref[image](IMG-ORDER1)`

### REQ-4.5 Keep an unpaid order when cancellation is declined

In "Cancel order"(role=dialog), "Keep order"(role=button) closes confirmation without mutation. "Payment status"(role=region) retains Pending payment and Pay now for the identified order_read order. Only confirmed cancellation closes the order.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

Dates and time-dependent behavior use Asia/Shanghai and the shared application/evaluator time 2026-07-19T08:00:00+08:00; public countdowns use elapsed time.

Order entries are uniquely named Record <order number> within Order list, and row actions affect only that identity. Display lifecycle states Not traveled and Pending review are distinct from payment state.

**IMG-ORDER2 · order_details**

![IMG-ORDER2 · order_details](reference/order2.png)

**IMG-ORDER1 · orders**

![IMG-ORDER1 · orders](reference/order1.png)

**Type:** ATOMIC
**Dependencies:** REQ-4.3

**Scenarios:**

- SCN-REQ-4.5-01 — Keep an unpaid order when cancellation is declined
  - **Step:** STEP-REQ-4.5-01-01
    - **Given:** order_read has signed in using ctrip_order_read@example.com / Travel1234 and checked Agree to terms, then opened My account → Orders. Its seeded orders are CTRIP20260721001/JD5162/¥530/Pending payment, CTRIP20260722002/CZ3401/¥390/Not traveled and CTRIP20260718003/MU5234/¥650/Pending review. View details has been clicked within CTRIP20260721001.
      Seed prerequisites (prepared before this scenario):
      - existing verified accounts: {"order_read": {"email": "ctrip_order_read@example.com", "password": "Travel1234"}}
      - historical and cancellation orders: [{"owner": "order_read", "number": "CTRIP20260721001", "flight": "JD5162", "date": "2026-07-21", "origin": "Chengdu", "destination": "Guangzhou", "total": 530, "payment_status": "Pending payment", "display_status": "Pending payment"}, {"owner": "order_read", "number": "CTRIP20260722002", "flight": "CZ3401", "date": "2026-07-22", "total": 390, "payment_status": "Paid", "display_status": "Not traveled"}, {"owner": "order_read", "number": "CTRIP20260718003", "flight": "MU5234", "date": "2026-07-18", "total": 650, "payment_status": "Paid", "display_status": "Pending review"}]
    - **When:** Click Cancel order in Payment status, then Keep order within the dialog.
    - **Then:** The dialog closes; CTRIP20260721001 remains identified with Pending payment and Pay now available.
    - **References:** `\ref[requirement](REQ-4.3)`, `\ref[image](IMG-ORDER2)`, `\ref[image](IMG-ORDER1)`

### REQ-4.6 Keep order lists scoped to the current account

Selecting "All orders"(role=tab) shows only the signed-in account's orders in "Order list"(role=region). Since profile_read owns none, its list must not borrow orders belonging to order_read or order_cancel.

Global navigation is a navigation landmark named Global navigation. Fields have associated labels; explicitly named tabs, radios, checkboxes, dialogs and fields retain their stated roles.

Dates and time-dependent behavior use Asia/Shanghai and the shared application/evaluator time 2026-07-19T08:00:00+08:00; public countdowns use elapsed time.

Order entries are uniquely named Record <order number> within Order list, and row actions affect only that identity. Display lifecycle states Not traveled and Pending review are distinct from payment state.

**IMG-ORDER1 · orders**

![IMG-ORDER1 · orders](reference/order1.png)

**Type:** ATOMIC
**Dependencies:** REQ-4.1

**Scenarios:**

- SCN-REQ-4.6-01 — Keep order lists scoped to the current account
  - **Step:** STEP-REQ-4.6-01-01
    - **Given:** profile_read has signed in as ctrip_profile_read@example.com / Travel1234 and opened Orders; this account owns no orders.
      Seed prerequisites (prepared before this scenario):
      - existing verified accounts: {"profile_read": {"email": "ctrip_profile_read@example.com", "password": "Travel1234", "mobile": "13800000013", "nickname": "Profile Reader", "real_name": "Li Ming", "gender": "Male", "birth_date": "1990-01-01"}}
    - **When:** Select All orders.
    - **Then:** Order list has no records and none of CTRIP20260721001, CTRIP20260722002, CTRIP20260718003 or CTRIP20260721004 are exposed from other accounts.
    - **References:** `\ref[requirement](REQ-4.1)`, `\ref[image](IMG-ORDER1)`
