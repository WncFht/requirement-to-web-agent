# 12306 railway travel

A railway ticketing system for searching trains, managing booking passengers, booking journeys, and paying for tickets.

Dates and times use Asia/Shanghai. The application, client, server and evaluator start at 2026-07-21T00:00:00+08:00; client and server clocks advance together with elapsed time.

## REQ-1 Account access

Support log in with username email or mobile capability, sign out and clear session.

**Type:** FOLDER
**Dependencies:** None

### REQ-1.1 Log in with username email or mobile capability

Support open credential login, authenticate traveler credentials.

**Type:** FOLDER
**Dependencies:** None

#### REQ-1.1.1 Open credential login

Follow Login from the public header. The login page displays Email/Username/Mobile number, Password, and LOGIN without authenticating merely by navigation.

**IMG-HOMEPAGE · home**

![IMG-HOMEPAGE · home](reference/homepage.png)

**IMG-LOGIN · login**

![IMG-LOGIN · login](reference/login.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-1.1.1-01 — Open credential login
  - **Step:** STEP-REQ-1.1.1-01-01
    - **Given:** A signed-out visitor is on the public homepage.
    - **When:** Follow Login from the public header.
    - **Then:** The login page displays Email/Username/Mobile number, Password, and LOGIN without authenticating merely by navigation.
    - **References:** `\ref[image](IMG-HOMEPAGE)`, `\ref[image](IMG-LOGIN)`

#### REQ-1.1.2 Authenticate traveler credentials

"Login"(role=link) opens credential login. A logged-out traveler enters a username, email, or mobile in "Email/Username/Mobile number"(role=textbox), enters "Password"(role=textbox), and clicks "LOGIN"(role=button). Correct credentials establish the same account's persisted session; incorrect credentials leave the user logged out under the capability's declared errors. Either missing account or missing password independently triggers the required-credentials error, even if the other field is supplied.

Verified accounts have Password123!, usernames/emails from the retained scenarios, and a distinct holder passport. registered_user can also log in as registered_user@example.com or 13800000010. Login persists and shows a status containing Login successful; navigation exposes Booking, My 12306 and Sign Out. Empty credentials show Please enter your username/email/phone number and password.; unknown accounts show User not found.; wrong passwords show Incorrect password.. Registration links and their workflows are outside scope.

**IMG-LOGIN · login**

![IMG-LOGIN · login](reference/login.png)

**IMG-HOMEPAGE · home**

![IMG-HOMEPAGE · home](reference/homepage.png)

**Type:** ATOMIC
**Dependencies:** REQ-1.1.1

**Scenarios:**

- SCN-REQ-1.1.2-01 — Authenticate by username email and mobile
  - **Step:** STEP-REQ-1.1.2-01-01
    - **Given:** The visitor is logged out on the homepage; the benchmark clock is 2026-07-21 00:00 Asia/Shanghai. The verified registered_user identity has email registered_user@example.com, mobile 13800000010 and password Password123!.
      Seed prerequisites (prepared before this scenario):
      - verified account directory: {"accounts": [{"username": "registered_user", "email": "registered_user@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult"}], "specific_identity": {"registered_user": {"passport": "P20260010", "mobile": "13800000010"}}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
    - **When:** For each of registered_user, registered_user@example.com and 13800000010, open Login, enter the identity and Password123! and click LOGIN; reload after each successful login and then click Sign Out before trying the next identity.
    - **Then:** Each identity displays Login successful and Sign Out persists after reload; each sign-out restores Login and removes Sign Out.
    - **References:** `\ref[requirement](REQ-1.1.1)`, `\ref[image](IMG-LOGIN)`, `\ref[image](IMG-HOMEPAGE)`
- SCN-REQ-1.1.2-02 — Reject empty credentials
  - **Step:** STEP-REQ-1.1.2-02-01
    - **Given:** The visitor is logged out on the homepage; the benchmark clock is 2026-07-21 00:00 Asia/Shanghai.
    - **When:** Open Login, leave Email/Username/Mobile number and Password empty and click LOGIN.
    - **Then:** Please enter your username/email/phone number and password. appears and Sign Out remains unavailable.
    - **References:** `\ref[requirement](REQ-1.1.1)`, `\ref[image](IMG-LOGIN)`, `\ref[image](IMG-HOMEPAGE)`
- SCN-REQ-1.1.2-03 — Reject unknown account
  - **Step:** STEP-REQ-1.1.2-03-01
    - **Given:** The visitor is logged out on the homepage; the benchmark clock is 2026-07-21 00:00 Asia/Shanghai. unknown_account does not exist.
    - **When:** Open Login, enter unknown_account and Password123!, and click LOGIN.
    - **Then:** User not found. appears and Sign Out remains unavailable.
    - **References:** `\ref[requirement](REQ-1.1.1)`, `\ref[image](IMG-LOGIN)`, `\ref[image](IMG-HOMEPAGE)`
- SCN-REQ-1.1.2-04 — Reject wrong password
  - **Step:** STEP-REQ-1.1.2-04-01
    - **Given:** The visitor is logged out on the homepage; the benchmark clock is 2026-07-21 00:00 Asia/Shanghai. registered_user exists with Password123!.
      Seed prerequisites (prepared before this scenario):
      - verified account directory: {"accounts": [{"username": "registered_user", "email": "registered_user@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult"}], "specific_identity": {"registered_user": {"passport": "P20260010", "mobile": "13800000010"}}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
    - **When:** Open Login, enter registered_user and WrongPassword123!, and click LOGIN.
    - **Then:** Incorrect password. appears and Sign Out remains unavailable.
    - **References:** `\ref[requirement](REQ-1.1.1)`, `\ref[image](IMG-LOGIN)`, `\ref[image](IMG-HOMEPAGE)`
- SCN-REQ-1.1.2-05 — Reject missing password
  - **Step:** STEP-REQ-1.1.2-05-01
    - **Given:** The visitor is logged out on the homepage; the benchmark clock is 2026-07-21 00:00 Asia/Shanghai. registered_user exists.
      Seed prerequisites (prepared before this scenario):
      - verified account directory: {"accounts": [{"username": "registered_user", "email": "registered_user@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult"}], "specific_identity": {"registered_user": {"passport": "P20260010", "mobile": "13800000010"}}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
    - **When:** Open Login, enter registered_user, leave Password empty and click LOGIN.
    - **Then:** Please enter your username/email/phone number and password. appears and Sign Out remains unavailable.
    - **References:** `\ref[requirement](REQ-1.1.1)`, `\ref[image](IMG-LOGIN)`, `\ref[image](IMG-HOMEPAGE)`
- SCN-REQ-1.1.2-06 — Reject missing account
  - **Step:** STEP-REQ-1.1.2-06-01
    - **Given:** The visitor is logged out on the homepage; the benchmark clock is 2026-07-21 00:00 Asia/Shanghai.
    - **When:** Open Login, leave Email/Username/Mobile number empty, enter Password123! in Password and click LOGIN.
    - **Then:** Please enter your username/email/phone number and password. appears and Sign Out remains unavailable.
    - **References:** `\ref[requirement](REQ-1.1.1)`, `\ref[image](IMG-LOGIN)`, `\ref[image](IMG-HOMEPAGE)`

### REQ-1.2 Sign out and clear session

Successful login replaces the top Register entry with "Sign Out"(role=link). Clicking it clears persisted authentication, displays successful logout feedback, and restores "Register"(role=link) and "Login"(role=link) in place of Sign Out and the username.

**IMG-HOMEPAGE · home**

![IMG-HOMEPAGE · home](reference/homepage.png)

**IMG-LOGIN · login**

![IMG-LOGIN · login](reference/login.png)

**Type:** ATOMIC
**Dependencies:** REQ-1.1.2

**Scenarios:**

- SCN-REQ-1.2-01 — Clear persisted login
  - **Step:** STEP-REQ-1.2-01-01
    - **Given:** registered_user has signed in through Login with Password123! and Sign Out is visible.
      Seed prerequisites (prepared before this scenario):
      - verified account directory: {"accounts": [{"username": "registered_user", "email": "registered_user@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult"}], "specific_identity": {"registered_user": {"passport": "P20260010", "mobile": "13800000010"}}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
    - **When:** Click Sign Out, inspect logout feedback, then reload.
    - **Then:** Logout successful. appears; after reload Login and Register are visible and Sign Out is unavailable.
    - **References:** `\ref[requirement](REQ-1.1.2)`, `\ref[image](IMG-HOMEPAGE)`, `\ref[image](IMG-LOGIN)`

## REQ-2 Train search

Support choose locations and departure date capability, search direct trains and reject incomplete route, inspect fares and empty direct route, change travel date from results, sort direct train results, filter train type stations and departure interval, open default ticket search from navigation.

**Type:** FOLDER
**Dependencies:** None

### REQ-2.1 Choose locations and departure date capability

Support open public station and date selectors, choose a departure location, choose and validate departure date.

**Type:** FOLDER
**Dependencies:** None

#### REQ-2.1.1 Open public station and date selectors

Focus From and then reopen the homepage and focus Date. From exposes Popular and ABCDE tabs; Date exposes the declared 2026-07-21 date choice; Search remains available.

**IMG-LOCATION-SELECTOR-LIST · home**

![IMG-LOCATION-SELECTOR-LIST · home](reference/location-selector-list.png)

**IMG-LOCATION-SELECTOR-FORM · home**

![IMG-LOCATION-SELECTOR-FORM · home](reference/location-selector-form.png)

**IMG-DATE-SELECTOR · home**

![IMG-DATE-SELECTOR · home](reference/date-selector.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-2.1.1-01 — Open public station and date selectors
  - **Step:** STEP-REQ-2.1.1-01-01
    - **Given:** A visitor is on the public homepage.
    - **When:** Focus From and then reopen the homepage and focus Date.
    - **Then:** From exposes Popular and ABCDE tabs; Date exposes the declared 2026-07-21 date choice; Search remains available.
    - **References:** `\ref[image](IMG-LOCATION-SELECTOR-LIST)`, `\ref[image](IMG-LOCATION-SELECTOR-FORM)`, `\ref[image](IMG-DATE-SELECTOR)`

#### REQ-2.1.2 Choose a departure location

On public search, "From"(role=textbox) supports station selection through pinyin, Chinese, or alphabetical browsing. "Popular"(role=tab), "ABCDE"(role=tab), "FGHIJ"(role=tab), "KLMNO"(role=tab), "PQRST"(role=tab), and "UVWXYZ"(role=tab) provide the declared groups; matching suggestions such as "Shanghai (上海)"(role=button) and "Beijing (北京)"(role=button) are unique. Choosing a station fills its canonical English city name.

**IMG-HOMEPAGE · home**

![IMG-HOMEPAGE · home](reference/homepage.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.1.1

**Scenarios:**

- SCN-REQ-2.1.2-01 — Choose Shanghai using pinyin and Chinese
  - **Step:** STEP-REQ-2.1.2-01-01
    - **Given:** The visitor is logged out on the homepage; the benchmark clock is 2026-07-21 00:00 Asia/Shanghai.
      Seed prerequisites (prepared before this scenario):
      - station directory: {"locations": ["Shanghai (上海)"]}
    - **When:** Enter shang in From, choose Shanghai (上海), then repeat with 上海 and choose the same suggestion.
    - **Then:** Each query shows Top destinations and exactly one Shanghai (上海) button; choosing it sets From to canonical Shanghai.
    - **References:** `\ref[requirement](REQ-2.1.1)`, `\ref[image](IMG-HOMEPAGE)`
- SCN-REQ-2.1.2-02 — Choose Beijing from alphabetical selector
  - **Step:** STEP-REQ-2.1.2-02-01
    - **Given:** The visitor is logged out on the homepage; the benchmark clock is 2026-07-21 00:00 Asia/Shanghai.
      Seed prerequisites (prepared before this scenario):
      - station directory: {"locations": ["Shanghai (上海)", "Beijing (北京)"]}
    - **When:** Click From, inspect Popular/ABCDE/FGHIJ/KLMNO/PQRST/UVWXYZ tabs, select ABCDE and click Beijing (北京).
    - **Then:** The tabs are visible; Beijing (北京) is unique in the selected group and From becomes Beijing.
    - **References:** `\ref[requirement](REQ-2.1.1)`, `\ref[image](IMG-HOMEPAGE)`

#### REQ-2.1.3 Choose and validate departure date

Opening "Date"(role=textbox) exposes full-date choices, including "2026-07-21"(role=button), which fills the selected date. The sale window July 21 through August 4 is inclusive. "Search"(role=button) rejects dates outside that window with the declared message and retains the homepage form.

**IMG-HOMEPAGE · home**

![IMG-HOMEPAGE · home](reference/homepage.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.1.1

**Scenarios:**

- SCN-REQ-2.1.3-01 — Select departure date
  - **Step:** STEP-REQ-2.1.3-01-01
    - **Given:** The visitor is logged out on the homepage; the benchmark clock is 2026-07-21 00:00 Asia/Shanghai.
    - **When:** Open Date and click the full-date button 2026-07-21.
    - **Then:** Date contains 2026-07-21.
    - **References:** `\ref[requirement](REQ-2.1.1)`, `\ref[image](IMG-HOMEPAGE)`
- SCN-REQ-2.1.3-02 — Reject past date
  - **Step:** STEP-REQ-2.1.3-02-01
    - **Given:** The visitor is logged out on the homepage; the benchmark clock is 2026-07-21 00:00 Asia/Shanghai.
    - **When:** Enter 2026-07-20 in Date and click Search.
    - **Then:** Please choose a departure date from 2026-07-21 through 2026-08-04. appears and Ticket search remains visible.
    - **References:** `\ref[requirement](REQ-2.1.1)`, `\ref[image](IMG-HOMEPAGE)`
- SCN-REQ-2.1.3-03 — Reject date beyond sale window
  - **Step:** STEP-REQ-2.1.3-03-01
    - **Given:** The visitor is logged out on the homepage; the benchmark clock is 2026-07-21 00:00 Asia/Shanghai.
    - **When:** Enter 2026-08-05 in Date and click Search.
    - **Then:** Please choose a departure date from 2026-07-21 through 2026-08-04. appears and Ticket search remains visible.
    - **References:** `\ref[requirement](REQ-2.1.1)`, `\ref[image](IMG-HOMEPAGE)`

### REQ-2.2 Search direct trains and reject incomplete route

Users choose locations in "From"(role=textbox) and "To"(role=textbox), set "Date"(role=textbox), and click "Search"(role=button). Shanghai–Beijing on 2026-07-21 opens results preserving those inputs, the route summary Shanghai (上海) - Beijing (北京), and a visible count, including G1001. Empty From shows Please enter a valid departure place. even when the other criteria are valid; empty To likewise shows Please enter a valid arrival place. Results remain below homepage navigation and provide "Travel dates"(role=region) with full YYYY-MM-DD actions, "Filter"(role=region), booking actions, and columns Train No., Departure Time, Travel time, Arrival Time, and Price. Published matches on the current and following day include distinct types, times, durations, prices, stations, and inventory, covering G/C/D and Other, Shanghai Hongqiao departure, Beijing South arrival, and 06:00-12:00 departures. Business-class, First-class, Second-class, and Standing ticket prices and both available and unavailable inventories remain observable. The default Beijing–Shanghai route is also populated for the current date.

Train numbers in results are independently identifiable visible text.

Every result train number is independently identifiable visible text; filtering and sorting affect the current search selection, not the underlying published services.

**IMG-HOMEPAGE · home**

![IMG-HOMEPAGE · home](reference/homepage.png)

**IMG-SEARCH-RESULT · train_results**

![IMG-SEARCH-RESULT · train_results](reference/search-result.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.1.2, REQ-2.1.3

**Scenarios:**

- SCN-REQ-2.2-01 — Show matching trains and preserve criteria
  - **Step:** STEP-REQ-2.2-01-01
    - **Given:** The visitor is logged out on the homepage; the benchmark clock is 2026-07-21 00:00 Asia/Shanghai. The published timetable contains G1001, G1002 and K1003 for Shanghai–Beijing on July 21.
      Seed prerequisites (prepared before this scenario):
      - station directory: {"locations": ["Shanghai (上海)", "Beijing (北京)"]}
      - published services: {"Shanghai-Beijing": {"2026-07-21": [{"number": "G1001", "from_station": "Shanghai Hongqiao", "to_station": "Beijing South", "departure": "08:00", "arrival": "13:00", "duration": 300, "second_price": 576}, {"number": "G1002", "from_station": "Shanghai", "to_station": "Beijing", "departure": "13:00", "arrival": "19:00", "duration": 360, "second_price": 600}, {"number": "K1003", "from_station": "Shanghai", "to_station": "Beijing South", "departure": "00:30", "arrival": "15:30", "duration": 900, "second_price": 200}]}, "G1001_seats": {"business": {"price": 1870, "discount": "32% off", "available": 1}, "first": {"price": 967, "discount": "24% off", "available": 0}, "second": {"price": 576, "discount": "27% off", "available": 0}, "standing": {"price": 576, "discount": "27% off", "available": "Enough"}}, "allocation": "One independent business seat per scenario account; additional passengers and all current orders are created through the retained UI flows."}
    - **When:** Enter shang in From and choose Shanghai (上海), enter bei in To and choose Beijing (北京), open Date and choose 2026-07-21, then click Search.
    - **Then:** From/To/Date preserve Shanghai/Beijing/2026-07-21; Shanghai (上海) - Beijing (北京) and 3 results appear with exactly G1001, G1002 and K1003; Travel dates, Filter and Train No./Departure Time/Travel time/Arrival Time/Price columns are visible.
    - **References:** `\ref[requirement](REQ-2.1.2)`, `\ref[requirement](REQ-2.1.3)`, `\ref[image](IMG-HOMEPAGE)`, `\ref[image](IMG-SEARCH-RESULT)`
- SCN-REQ-2.2-02 — Reject empty From
  - **Step:** STEP-REQ-2.2-02-01
    - **Given:** The visitor is logged out on the homepage; the benchmark clock is 2026-07-21 00:00 Asia/Shanghai.
      Seed prerequisites (prepared before this scenario):
      - station directory: {"locations": ["Shanghai (上海)", "Beijing (北京)"]}
    - **When:** Leave From empty, choose Beijing (北京) for To, choose Date 2026-07-21 and click Search.
    - **Then:** Please enter a valid departure place. appears and Ticket search remains visible.
    - **References:** `\ref[requirement](REQ-2.1.2)`, `\ref[requirement](REQ-2.1.3)`, `\ref[image](IMG-HOMEPAGE)`, `\ref[image](IMG-SEARCH-RESULT)`
- SCN-REQ-2.2-03 — Reject empty To
  - **Step:** STEP-REQ-2.2-03-01
    - **Given:** The visitor is logged out on the homepage; the benchmark clock is 2026-07-21 00:00 Asia/Shanghai.
      Seed prerequisites (prepared before this scenario):
      - station directory: {"locations": ["Shanghai (上海)", "Beijing (北京)"]}
    - **When:** Choose Shanghai (上海) for From, leave To empty, choose Date 2026-07-21 and click Search.
    - **Then:** Please enter a valid arrival place. appears and Ticket search remains visible.
    - **References:** `\ref[requirement](REQ-2.1.2)`, `\ref[requirement](REQ-2.1.3)`, `\ref[image](IMG-HOMEPAGE)`, `\ref[image](IMG-SEARCH-RESULT)`

### REQ-2.3 Inspect fares and empty direct route

Support inspect a fare and booking availability, observe a route without direct trains.

**Type:** FOLDER
**Dependencies:** None

#### REQ-2.3.1 Inspect a fare and booking availability

After a direct search, users inspect G1001's second-class fare CNY 576 despite its unavailable second-class inventory. "Book"(role=button) remains enabled because another class has seats.

Train numbers in results are independently identifiable visible text.

Each train row has a "Price" cell with seat type, price and a corresponding "Book" button. The seeded train "G1001" on the Shanghai-to-Beijing route shows the Second-class seat price as CNY 576 (the same fare displayed as ￥576.0 on its booking form, even though no second-class seats remain) and has an enabled "Book" button in its row because other seat classes are available.

Every result train number is independently identifiable visible text; filtering and sorting affect the current search selection, not the underlying published services.

**IMG-SEARCH-RESULT · train_results**

![IMG-SEARCH-RESULT · train_results](reference/search-result.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.2

**Scenarios:**

- SCN-REQ-2.3.1-01 — Show fare with bookable other class
  - **Step:** STEP-REQ-2.3.1-01-01
    - **Given:** The visitor has searched Shanghai to Beijing for 2026-07-21 through From, To, Date and Search; published results are G1001, G1002 and K1003. G1001 has no second-class seats but another class has inventory.
      Seed prerequisites (prepared before this scenario):
      - station directory: {"locations": ["Shanghai (上海)", "Beijing (北京)"]}
      - published services: {"Shanghai-Beijing": {"2026-07-21": [{"number": "G1001", "from_station": "Shanghai Hongqiao", "to_station": "Beijing South", "departure": "08:00", "arrival": "13:00", "duration": 300, "second_price": 576}, {"number": "G1002", "from_station": "Shanghai", "to_station": "Beijing", "departure": "13:00", "arrival": "19:00", "duration": 360, "second_price": 600}, {"number": "K1003", "from_station": "Shanghai", "to_station": "Beijing South", "departure": "00:30", "arrival": "15:30", "duration": 900, "second_price": 200}]}, "G1001_seats": {"business": {"price": 1870, "discount": "32% off", "available": 1}, "first": {"price": 967, "discount": "24% off", "available": 0}, "second": {"price": 576, "discount": "27% off", "available": 0}, "standing": {"price": 576, "discount": "27% off", "available": "Enough"}}, "allocation": "One independent business seat per scenario account; additional passengers and all current orders are created through the retained UI flows."}
    - **When:** Inspect G1001 and its Book action.
    - **Then:** G1001 displays Second-class seat and CNY 576; Book remains enabled because another class is available.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-SEARCH-RESULT)`

#### REQ-2.3.2 Observe a route without direct trains

Searching valid Shanghai–Lhasa on July 21 retains the selected criteria and displays No trains, 0 results, and the declared empty-result message without direct-train rows.

Train numbers in results are independently identifiable visible text.

The valid Shanghai-to-Lhasa route has no direct trains on 2026-07-21. Its results page preserves the search fields, shows a visible image named "No trains", the exact count "0 results", and the message "sorry, according to your inquiry condition, there is no train at present.".

Every result train number is independently identifiable visible text; filtering and sorting affect the current search selection, not the underlying published services.

**IMG-HOMEPAGE · home**

![IMG-HOMEPAGE · home](reference/homepage.png)

**IMG-SEARCH-RESULT · train_results**

![IMG-SEARCH-RESULT · train_results](reference/search-result.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.2

**Scenarios:**

- SCN-REQ-2.3.2-01 — Show no direct trains
  - **Step:** STEP-REQ-2.3.2-01-01
    - **Given:** The visitor is logged out on the homepage; the benchmark clock is 2026-07-21 00:00 Asia/Shanghai. No direct Shanghai–Lhasa services are published for July 21.
      Seed prerequisites (prepared before this scenario):
      - station directory: {"locations": ["Shanghai (上海)", "Lhasa (拉萨)"]}
      - published services: {"Shanghai-Lhasa": {"2026-07-21": []}, "allocation": "One independent business seat per scenario account; additional passengers and all current orders are created through the retained UI flows."}
    - **When:** Choose Shanghai (上海) in From and Lhasa (拉萨) in To, select Date 2026-07-21 and click Search.
    - **Then:** The criteria remain Shanghai/Lhasa/2026-07-21; No trains image, 0 results and sorry, according to your inquiry condition, there is no train at present. appear, and no train result rows remain.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-HOMEPAGE)`, `\ref[image](IMG-SEARCH-RESULT)`

### REQ-2.4 Change travel date from results

Support resubmit a changed results-page departure date.

**Type:** FOLDER
**Dependencies:** None

#### REQ-2.4.1 Resubmit a changed results-page departure date

From populated results, users open "Date"(role=textbox), choose "2026-07-22"(role=button), and click "Search"(role=button). The list is replaced with the matching July 22 services while preserving the route.

Train numbers in results are independently identifiable visible text.

The results page exposes a date input labelled "Date" and a "Search" button. Searching Shanghai to Beijing for 2026-07-22 replaces the displayed departure date with 2026-07-22 and shows the seeded train "G1001" for that date.

Every result train number is independently identifiable visible text; filtering and sorting affect the current search selection, not the underlying published services.

**IMG-SEARCH-RESULT · train_results**

![IMG-SEARCH-RESULT · train_results](reference/search-result.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.2

**Scenarios:**

- SCN-REQ-2.4.1-01 — Change date using date picker
  - **Step:** STEP-REQ-2.4.1-01-01
    - **Given:** The visitor has searched Shanghai to Beijing for 2026-07-21 through From, To, Date and Search; published results are G1001, G1002 and K1003. July 22 additionally contains G2002.
      Seed prerequisites (prepared before this scenario):
      - station directory: {"locations": ["Shanghai (上海)", "Beijing (北京)"]}
      - published services: {"Shanghai-Beijing": {"2026-07-21": [{"number": "G1001", "from_station": "Shanghai Hongqiao", "to_station": "Beijing South", "departure": "08:00", "arrival": "13:00", "duration": 300, "second_price": 576}, {"number": "G1002", "from_station": "Shanghai", "to_station": "Beijing", "departure": "13:00", "arrival": "19:00", "duration": 360, "second_price": 600}, {"number": "K1003", "from_station": "Shanghai", "to_station": "Beijing South", "departure": "00:30", "arrival": "15:30", "duration": 900, "second_price": 200}], "2026-07-22": [{"number": "G1001", "from_station": "Shanghai Hongqiao", "to_station": "Beijing South", "departure": "08:00", "arrival": "13:00", "duration": 300, "second_price": 576}, {"number": "G1002", "from_station": "Shanghai", "to_station": "Beijing", "departure": "13:00", "arrival": "19:00", "duration": 360, "second_price": 600}, {"number": "K1003", "from_station": "Shanghai", "to_station": "Beijing South", "departure": "00:30", "arrival": "15:30", "duration": 900, "second_price": 200}, {"number": "G2002", "from_station": "Shanghai", "to_station": "Beijing", "departure": "10:00", "arrival": "15:00", "duration": 300, "second_price": 576}]}, "allocation": "One independent business seat per scenario account; additional passengers and all current orders are created through the retained UI flows."}
    - **When:** Open Date, click 2026-07-22 and click Search.
    - **Then:** Date becomes 2026-07-22 and results are replaced by G1001, G1002, K1003 and G2002.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-SEARCH-RESULT)`

### REQ-2.5 Sort direct train results

Support sort direct trains by departure time.

**Type:** FOLDER
**Dependencies:** None

#### REQ-2.5.1 Sort direct trains by departure time

Clicking "Departure Time"(role=button) on existing direct-train results orders them by published departure time ascending; clicking again reverses the order. Both operations preserve the complete current result set.

Train numbers in results are independently identifiable visible text.

The "Departure Time" table header contains a button named "Departure Time". Activating it once sorts visible train rows by departure time ascending, and activating it again sorts them descending.

Every result train number is independently identifiable visible text; filtering and sorting affect the current search selection, not the underlying published services.

**IMG-SEARCH-RESULT · train_results**

![IMG-SEARCH-RESULT · train_results](reference/search-result.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.2

**Scenarios:**

- SCN-REQ-2.5.1-01 — Toggle Departure Time sorting
  - **Step:** STEP-REQ-2.5.1-01-01
    - **Given:** The visitor has searched Shanghai to Beijing for 2026-07-21 through From, To, Date and Search; published results are G1001, G1002 and K1003. Departure times are K1003 00:30, G1001 08:00 and G1002 13:00.
      Seed prerequisites (prepared before this scenario):
      - station directory: {"locations": ["Shanghai (上海)", "Beijing (北京)"]}
      - published services: {"Shanghai-Beijing": {"2026-07-21": [{"number": "G1001", "from_station": "Shanghai Hongqiao", "to_station": "Beijing South", "departure": "08:00", "arrival": "13:00", "duration": 300, "second_price": 576}, {"number": "G1002", "from_station": "Shanghai", "to_station": "Beijing", "departure": "13:00", "arrival": "19:00", "duration": 360, "second_price": 600}, {"number": "K1003", "from_station": "Shanghai", "to_station": "Beijing South", "departure": "00:30", "arrival": "15:30", "duration": 900, "second_price": 200}]}, "allocation": "One independent business seat per scenario account; additional passengers and all current orders are created through the retained UI flows."}
    - **When:** Click Departure Time in its columnheader, inspect order, then click it again.
    - **Then:** The first order is K1003, G1001, G1002; the second is G1002, G1001, K1003, retaining all three services.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-SEARCH-RESULT)`

### REQ-2.6 Filter trains by type

Support filter direct trains by type.

**Type:** FOLDER
**Dependencies:** None

#### REQ-2.6.1 Filter direct trains by type

Within "Filter"(role=region) and "Train type"(role=group), selecting "G/C/D"(role=checkbox) retains matching train prefixes and excludes Other. Selecting "Other"(role=checkbox) restricts the list to published non-G/C/D types. "All"(role=checkbox) removes the type restriction and restores both groups for the current route and date. Published matches and nonmatches make each effect observable.

Train numbers in results are independently identifiable visible text.

The "Filter" region contains a group named "Train type" with checkboxes "All", "G/C/D", and "Other". Selecting "G/C/D" shows at least one train and restricts visible train numbers to G, C, or D prefixes.

Every result train number is independently identifiable visible text; filtering and sorting affect the current search selection, not the underlying published services.

**IMG-SEARCH-RESULT · train_results**

![IMG-SEARCH-RESULT · train_results](reference/search-result.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.2

**Scenarios:**

- SCN-REQ-2.6.1-01 — Restrict train type
  - **Step:** STEP-REQ-2.6.1-01-01
    - **Given:** The visitor has searched Shanghai to Beijing for 2026-07-21 through From, To, Date and Search; published results are G1001, G1002 and K1003.
      Seed prerequisites (prepared before this scenario):
      - station directory: {"locations": ["Shanghai (上海)", "Beijing (北京)"]}
      - published services: {"Shanghai-Beijing": {"2026-07-21": [{"number": "G1001", "from_station": "Shanghai Hongqiao", "to_station": "Beijing South", "departure": "08:00", "arrival": "13:00", "duration": 300, "second_price": 576}, {"number": "G1002", "from_station": "Shanghai", "to_station": "Beijing", "departure": "13:00", "arrival": "19:00", "duration": 360, "second_price": 600}, {"number": "K1003", "from_station": "Shanghai", "to_station": "Beijing South", "departure": "00:30", "arrival": "15:30", "duration": 900, "second_price": 200}]}, "allocation": "One independent business seat per scenario account; additional passengers and all current orders are created through the retained UI flows."}
    - **When:** Check G/C/D within Filter → Train type (group).
    - **Then:** The result set is exactly G1001 and G1002; K1003 is excluded.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-SEARCH-RESULT)`
- SCN-REQ-2.6.1-02 — Filter Other train types
  - **Step:** STEP-REQ-2.6.1-02-01
    - **Given:** The visitor has searched Shanghai to Beijing for 2026-07-21 through From, To, Date and Search; published results are G1001, G1002 and K1003.
      Seed prerequisites (prepared before this scenario):
      - station directory: {"locations": ["Shanghai (上海)", "Beijing (北京)"]}
      - published services: {"Shanghai-Beijing": {"2026-07-21": [{"number": "G1001", "from_station": "Shanghai Hongqiao", "to_station": "Beijing South", "departure": "08:00", "arrival": "13:00", "duration": 300, "second_price": 576}, {"number": "G1002", "from_station": "Shanghai", "to_station": "Beijing", "departure": "13:00", "arrival": "19:00", "duration": 360, "second_price": 600}, {"number": "K1003", "from_station": "Shanghai", "to_station": "Beijing South", "departure": "00:30", "arrival": "15:30", "duration": 900, "second_price": 200}]}, "allocation": "One independent business seat per scenario account; additional passengers and all current orders are created through the retained UI flows."}
    - **When:** Check Other within Filter → Train type (group).
    - **Then:** The result set is exactly K1003; both G trains are excluded.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-SEARCH-RESULT)`
- SCN-REQ-2.6.1-03 — Restore all train types
  - **Step:** STEP-REQ-2.6.1-03-01
    - **Given:** The visitor has searched Shanghai to Beijing for 2026-07-21 through From, To, Date and Search; published results are G1001, G1002 and K1003.
      Seed prerequisites (prepared before this scenario):
      - station directory: {"locations": ["Shanghai (上海)", "Beijing (北京)"]}
      - published services: {"Shanghai-Beijing": {"2026-07-21": [{"number": "G1001", "from_station": "Shanghai Hongqiao", "to_station": "Beijing South", "departure": "08:00", "arrival": "13:00", "duration": 300, "second_price": 576}, {"number": "G1002", "from_station": "Shanghai", "to_station": "Beijing", "departure": "13:00", "arrival": "19:00", "duration": 360, "second_price": 600}, {"number": "K1003", "from_station": "Shanghai", "to_station": "Beijing South", "departure": "00:30", "arrival": "15:30", "duration": 900, "second_price": 200}]}, "allocation": "One independent business seat per scenario account; additional passengers and all current orders are created through the retained UI flows."}
    - **When:** Check G/C/D in Train type, verify the restricted result set, then check All.
    - **Then:** G/C/D first leaves G1001 and G1002; All restores G1001, G1002 and K1003.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-SEARCH-RESULT)`

### REQ-2.7 Open default ticket search from navigation

Hovering "Booking"(role=link) in homepage navigation reveals "Tickets"(role=link). Activating Tickets opens populated default Beijing–Shanghai results for 2026-07-21, with From, To, and Date reflecting that route and day.

Train numbers in results are independently identifiable visible text.

Every result train number is independently identifiable visible text; filtering and sorting affect the current search selection, not the underlying published services.

**IMG-HOMEPAGE · home**

![IMG-HOMEPAGE · home](reference/homepage.png)

**IMG-SEARCH-RESULT · train_results**

![IMG-SEARCH-RESULT · train_results](reference/search-result.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.2

**Scenarios:**

- SCN-REQ-2.7-01 — Open Tickets quick entry
  - **Step:** STEP-REQ-2.7-01-01
    - **Given:** The visitor is logged out on the homepage; the benchmark clock is 2026-07-21 00:00 Asia/Shanghai. The default Beijing–Shanghai timetable contains G3001 on July 21.
      Seed prerequisites (prepared before this scenario):
      - station directory: {"locations": ["Shanghai (上海)", "Beijing (北京)"]}
      - published services: {"Beijing-Shanghai": {"2026-07-21": [{"number": "G3001", "departure": "08:00", "arrival": "13:00", "duration": 300}]}, "G1001_seats": {"business": {"price": 1870, "discount": "32% off", "available": 1}, "first": {"price": 967, "discount": "24% off", "available": 0}, "second": {"price": 576, "discount": "27% off", "available": 0}, "standing": {"price": 576, "discount": "27% off", "available": "Enough"}}, "allocation": "One independent business seat per scenario account; additional passengers and all current orders are created through the retained UI flows."}
    - **When:** Hover Booking in navigation and activate Tickets.
    - **Then:** Populated default results include G3001; From is Beijing, To is Shanghai and Date is 2026-07-21.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-HOMEPAGE)`, `\ref[image](IMG-SEARCH-RESULT)`

## REQ-3 Personal center and orders

Support enter personal center with access control capability, browse order categories and empty-state booking routes capability, inspect and resume unpaid orders capability.

**Type:** FOLDER
**Dependencies:** None

### REQ-3.1 Enter personal center with access control capability

Support open authenticated personal center, enter personal center according to authentication.

**Type:** FOLDER
**Dependencies:** None

#### REQ-3.1.1 Open authenticated personal center

My 12306 sends an anonymous visitor to credential Login and an authenticated traveler to the personal center. Personal center menu is a navigation landmark exposing Personal Center, Order center, Personal and Information management links; Notice is a region showing the correct account name and a Notice image. Order center leads to Ticket orders; Information management leads to My Passengers. Personal is a navigation-only affordance; account/security editing is outside scope.

**IMG-HOMEPAGE · home**

![IMG-HOMEPAGE · home](reference/homepage.png)

**IMG-USER-CENTER · personal_center**

![IMG-USER-CENTER · personal_center](reference/user-center.png)

**Type:** ATOMIC
**Dependencies:** REQ-1.1.2

**Scenarios:**

- SCN-REQ-3.1.1-01 — Open authenticated personal center
  - **Step:** STEP-REQ-3.1.1-01-01
    - **Given:** The verified personal_center_user account is available.
      Seed prerequisites (prepared before this scenario):
      - verified account directory: {"accounts": [{"username": "personal_center_user__e029177424", "email": "personal_center_user__e029177424@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult", "display_name": "personal_center_user", "holder_name": "personal_center_user"}], "specific_identity": {"personal_center_user": {"mobile": "13800000020"}}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
      Scenario account identities: {"personal_center_user": "personal_center_user__e029177424"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Log in and follow My 12306 to the personal center.
    - **Then:** Personal center menu and Notice are visible, and Notice identifies personal_center_user.
    - **References:** `\ref[requirement](REQ-1.1.2)`, `\ref[image](IMG-HOMEPAGE)`, `\ref[image](IMG-USER-CENTER)`

#### REQ-3.1.2 Enter personal center according to authentication

My 12306 sends an anonymous visitor to credential Login and an authenticated traveler to the personal center. Personal center menu is a navigation landmark exposing Personal Center, Order center, Personal and Information management links; Notice is a region showing the correct account name and a Notice image. Order center leads to Ticket orders; Information management leads to My Passengers. Personal is a navigation-only affordance; account/security editing is outside scope.

**IMG-HOMEPAGE · home**

![IMG-HOMEPAGE · home](reference/homepage.png)

**IMG-LOGIN · login**

![IMG-LOGIN · login](reference/login.png)

**IMG-USER-CENTER · personal_center**

![IMG-USER-CENTER · personal_center](reference/user-center.png)

**Type:** ATOMIC
**Dependencies:** REQ-1.1.2

**Scenarios:**

- SCN-REQ-3.1.2-01 — Intercept logged-out personal center
  - **Step:** STEP-REQ-3.1.2-01-01
    - **Given:** The visitor is logged out on the homepage; the benchmark clock is 2026-07-21 00:00 Asia/Shanghai.
    - **When:** Activate My 12306.
    - **Then:** Login opens with Email/Username/Mobile number, Password and LOGIN instead of authenticated personal-center content.
    - **References:** `\ref[requirement](REQ-1.1.2)`, `\ref[requirement](REQ-3.1.1)`, `\ref[image](IMG-HOMEPAGE)`, `\ref[image](IMG-LOGIN)`, `\ref[image](IMG-USER-CENTER)`
- SCN-REQ-3.1.2-02 — Enter authenticated personal center
  - **Step:** STEP-REQ-3.1.2-02-01
    - **Given:** personal_center_user has signed in through Login with Password123!.
      Seed prerequisites (prepared before this scenario):
      - verified account directory: {"accounts": [{"username": "personal_center_user__d33ca86e66", "email": "personal_center_user__d33ca86e66@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult", "display_name": "personal_center_user", "holder_name": "personal_center_user"}], "specific_identity": {"personal_center_user": {"mobile": "13800000020"}}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
      Scenario account identities: {"personal_center_user": "personal_center_user__d33ca86e66"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Return Home and activate My 12306.
    - **Then:** Personal center menu contains Personal Center, Order center, Personal and Information management; Notice displays personal_center_user and its Notice image.
    - **References:** `\ref[requirement](REQ-1.1.2)`, `\ref[requirement](REQ-3.1.1)`, `\ref[image](IMG-HOMEPAGE)`, `\ref[image](IMG-LOGIN)`, `\ref[image](IMG-USER-CENTER)`

### REQ-3.2 Browse ticket-order categories

Support open ticket-order categories.

**Type:** FOLDER
**Dependencies:** None

#### REQ-3.2.1 Open ticket-order categories

Order center → Ticket orders opens the tabs Uncompleted orders, Upcoming trips and History orders. Selected tabs expose aria-selected=true and only their category is shown. Unpaid orders appear in Uncompleted orders; paid future journeys appear in Upcoming trips. History orders is only an entry affordance in this application; history filtering and historical order data are not required. orders_empty_user starts with no current orders.

**IMG-USER-CENTER · personal_center**

![IMG-USER-CENTER · personal_center](reference/user-center.png)

**IMG-TICKET-ORDERS · ticket_orders**

![IMG-TICKET-ORDERS · ticket_orders](reference/ticket-orders.png)

**Type:** ATOMIC
**Dependencies:** REQ-3.1.2

**Scenarios:**

- SCN-REQ-3.2.1-01 — Open ticket-order categories
  - **Step:** STEP-REQ-3.2.1-01-01
    - **Given:** The verified orders_empty_user account has no orders.
      Seed prerequisites (prepared before this scenario):
      - verified account directory: {"accounts": [{"username": "orders_empty_user__541dccecc4", "email": "orders_empty_user__541dccecc4@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult", "display_name": "orders_empty_user", "holder_name": "orders_empty_user"}], "specific_identity": {}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
      Scenario account identities: {"orders_empty_user": "orders_empty_user__541dccecc4"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Log in, follow Order center and Ticket orders, and select Uncompleted orders.
    - **Then:** The order view exposes Uncompleted orders, Upcoming trips, and History orders tabs.
    - **References:** `\ref[requirement](REQ-3.1.2)`, `\ref[image](IMG-USER-CENTER)`, `\ref[image](IMG-TICKET-ORDERS)`

### REQ-3.3 Inspect and resume unpaid orders capability

Support open unpaid-order view, inspect unpaid ticket orders, resume an unpaid order payment.

**Type:** FOLDER
**Dependencies:** None

#### REQ-3.3.1 Open unpaid-order view

Open Ticket orders and select Uncompleted orders. The unpaid G1001 row exposes Pay.

Uncompleted orders displays the UI-created G1001 order in a row identified by train/passenger. Columns are Train No., Departure date, Departure station, Arrival station and Operation. Each unpaid order has Pay, opening that same order in Order details and Payment information regions. Current orders are created through booking UI, not initially seeded.

**IMG-USER-CENTER · personal_center**

![IMG-USER-CENTER · personal_center](reference/user-center.png)

**IMG-UNCOMPLETED-ORDERS · ticket_orders**

![IMG-UNCOMPLETED-ORDERS · ticket_orders](reference/uncompleted-orders.png)

**Type:** ATOMIC
**Dependencies:** REQ-5.2.3.1, REQ-3.2.1

**Scenarios:**

- SCN-REQ-3.3.1-01 — Open unpaid-order view
  - **Step:** STEP-REQ-3.3.1-01-01
    - **Given:** An unpaid G1001 order is created through the declared booking flow for orders_unpaid_user.
      Seed prerequisites (prepared before this scenario):
      - published services: {"Shanghai-Beijing": {"2026-07-21": [{"number": "G1001", "from_station": "Shanghai Hongqiao", "to_station": "Beijing South", "departure": "08:00", "arrival": "13:00", "duration": 300, "second_price": 576}, {"number": "G1002", "from_station": "Shanghai", "to_station": "Beijing", "departure": "13:00", "arrival": "19:00", "duration": 360, "second_price": 600}, {"number": "K1003", "from_station": "Shanghai", "to_station": "Beijing South", "departure": "00:30", "arrival": "15:30", "duration": 900, "second_price": 200}]}, "G1001_seats": {"business": {"price": 1870, "discount": "32% off", "available": 1}, "first": {"price": 967, "discount": "24% off", "available": 0}, "second": {"price": 576, "discount": "27% off", "available": 0}, "standing": {"price": 576, "discount": "27% off", "available": "Enough"}}, "allocation": "One independent business seat per scenario account; additional passengers and all current orders are created through the retained UI flows."}
      - verified account directory: {"accounts": [{"username": "orders_unpaid_user__1ec57c26f1", "email": "orders_unpaid_user__1ec57c26f1@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult", "display_name": "orders_unpaid_user", "holder_name": "orders_unpaid_user"}], "specific_identity": {}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
      Scenario account identities: {"orders_unpaid_user": "orders_unpaid_user__1ec57c26f1"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Open Ticket orders and select Uncompleted orders.
    - **Then:** The unpaid G1001 row exposes Pay.
    - **References:** `\ref[requirement](REQ-3.1.2)`, `\ref[image](IMG-USER-CENTER)`, `\ref[image](IMG-UNCOMPLETED-ORDERS)`

#### REQ-3.3.2 Inspect unpaid ticket orders

Opening Uncompleted orders shows the UI-created unpaid G1001 row with route and the parent capability's required headers. Its "Pay"(role=button) provides payment access; matching "Order details"(role=region) and "Payment information"(role=region) identify the same unpaid order under the shared contract.

Uncompleted orders displays the UI-created G1001 order in a row identified by train/passenger. Columns are Train No., Departure date, Departure station, Arrival station and Operation. Each unpaid order has Pay, opening that same order in Order details and Payment information regions. Current orders are created through booking UI, not initially seeded.

**IMG-TICKET-ORDERS · ticket_orders**

![IMG-TICKET-ORDERS · ticket_orders](reference/ticket-orders.png)

**Type:** ATOMIC
**Dependencies:** REQ-3.3.1

**Scenarios:**

- SCN-REQ-3.3.2-01 — Inspect unpaid order table
  - **Step:** STEP-REQ-3.3.2-01-01
    - **Given:** orders_unpaid_user has created an unpaid G1001 order for 2026-07-21 through the passenger, search, booking and confirmation UI. Through UI, sign in with Password123!, create Passenger Example using Add new passengers with China, a distinct passport, expiration 2027-12-31, birth 2000-01-15, Female, Adult, passenger@example.com and 13800000040; search Shanghai–Beijing for the stated date, click Book on the stated train, check Passenger Example, select Business-class seat in that passenger row, click Place order and Confirm.
      Seed prerequisites (prepared before this scenario):
      - station directory: {"locations": ["Shanghai (上海)", "Beijing (北京)"]}
      - published services: {"Shanghai-Beijing": {"2026-07-21": [{"number": "G1001", "from_station": "Shanghai Hongqiao", "to_station": "Beijing South", "departure": "08:00", "arrival": "13:00", "duration": 300, "second_price": 576}, {"number": "G1002", "from_station": "Shanghai", "to_station": "Beijing", "departure": "13:00", "arrival": "19:00", "duration": 360, "second_price": 600}, {"number": "K1003", "from_station": "Shanghai", "to_station": "Beijing South", "departure": "00:30", "arrival": "15:30", "duration": 900, "second_price": 200}]}, "G1001_seats": {"business": {"price": 1870, "discount": "32% off", "available": 1}, "first": {"price": 967, "discount": "24% off", "available": 0}, "second": {"price": 576, "discount": "27% off", "available": 0}, "standing": {"price": 576, "discount": "27% off", "available": "Enough"}}, "allocation": "One independent business seat per scenario account; additional passengers and all current orders are created through the retained UI flows."}
      - verified account directory: {"accounts": [{"username": "orders_unpaid_user__c80b5ef98a", "email": "orders_unpaid_user__c80b5ef98a@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult", "display_name": "orders_unpaid_user", "holder_name": "orders_unpaid_user"}], "specific_identity": {}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
      Scenario account identities: {"orders_unpaid_user": "orders_unpaid_user__c80b5ef98a"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Open My 12306 → Order center → Ticket orders and select Uncompleted orders.
    - **Then:** Train No., Departure date, Departure station, Arrival station and Operation headers appear; G1001 displays Shanghai and Beijing with a Pay button.
    - **References:** `\ref[requirement](REQ-3.3.1)`, `\ref[requirement](REQ-5.2.3.1)`, `\ref[image](IMG-TICKET-ORDERS)`

#### REQ-3.3.3 Resume an unpaid order payment

Clicking "Pay"(role=button) on the identified unpaid G1001 order opens matching "Order details"(role=region) and "Payment information"(role=region), applying the parent capability's payment and identity rules.

Uncompleted orders displays the UI-created G1001 order in a row identified by train/passenger. Columns are Train No., Departure date, Departure station, Arrival station and Operation. Each unpaid order has Pay, opening that same order in Order details and Payment information regions. Current orders are created through booking UI, not initially seeded.

**IMG-TICKET-ORDERS · ticket_orders**

![IMG-TICKET-ORDERS · ticket_orders](reference/ticket-orders.png)

**IMG-PAYMENT · payment**

![IMG-PAYMENT · payment](reference/payment.png)

**Type:** ATOMIC
**Dependencies:** REQ-3.3.1, REQ-5.3

**Scenarios:**

- SCN-REQ-3.3.3-01 — Resume payment by order identity
  - **Step:** STEP-REQ-3.3.3-01-01
    - **Given:** orders_unpaid_user has created an unpaid G1001 order for 2026-07-21 through the passenger, search, booking and confirmation UI. Through UI, sign in with Password123!, create Passenger Example using Add new passengers with China, a distinct passport, expiration 2027-12-31, birth 2000-01-15, Female, Adult, passenger@example.com and 13800000040; search Shanghai–Beijing for the stated date, click Book on the stated train, check Passenger Example, select Business-class seat in that passenger row, click Place order and Confirm. Uncompleted orders is selected.
      Seed prerequisites (prepared before this scenario):
      - station directory: {"locations": ["Shanghai (上海)", "Beijing (北京)"]}
      - published services: {"Shanghai-Beijing": {"2026-07-21": [{"number": "G1001", "from_station": "Shanghai Hongqiao", "to_station": "Beijing South", "departure": "08:00", "arrival": "13:00", "duration": 300, "second_price": 576}, {"number": "G1002", "from_station": "Shanghai", "to_station": "Beijing", "departure": "13:00", "arrival": "19:00", "duration": 360, "second_price": 600}, {"number": "K1003", "from_station": "Shanghai", "to_station": "Beijing South", "departure": "00:30", "arrival": "15:30", "duration": 900, "second_price": 200}]}, "G1001_seats": {"business": {"price": 1870, "discount": "32% off", "available": 1}, "first": {"price": 967, "discount": "24% off", "available": 0}, "second": {"price": 576, "discount": "27% off", "available": 0}, "standing": {"price": 576, "discount": "27% off", "available": "Enough"}}, "allocation": "One independent business seat per scenario account; additional passengers and all current orders are created through the retained UI flows."}
      - verified account directory: {"accounts": [{"username": "orders_unpaid_user__ce3450b1ce", "email": "orders_unpaid_user__ce3450b1ce@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult", "display_name": "orders_unpaid_user", "holder_name": "orders_unpaid_user"}], "specific_identity": {}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
      Scenario account identities: {"orders_unpaid_user": "orders_unpaid_user__ce3450b1ce"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Click Pay within the G1001 row.
    - **Then:** Order details identifies G1001 and Payment information is visible for the resumed unpaid order.
    - **References:** `\ref[requirement](REQ-3.3.2)`, `\ref[requirement](REQ-5.3)`, `\ref[image](IMG-TICKET-ORDERS)`, `\ref[image](IMG-PAYMENT)`

## REQ-4 Passenger management

Support view passenger list with protected account holder, add and validate frequent passenger.

**Type:** FOLDER
**Dependencies:** None

### REQ-4.1 View passenger list with protected account holder

Information management → My Passengers shows a table with column headers All, Name, ID type, ID number, Mobile number and Operation. The account holder is initially present and has no Delete button. Additional passenger records are created through Add new passengers, uniquely identified by passport and visible name. Passenger maintenance deletion/search workflows are outside scope.

**IMG-USER-CENTER · personal_center**

![IMG-USER-CENTER · personal_center](reference/user-center.png)

**IMG-MY-PASSENGERS · passengers**

![IMG-MY-PASSENGERS · passengers](reference/my-passengers.png)

**Type:** ATOMIC
**Dependencies:** REQ-3.1.2

**Scenarios:**

- SCN-REQ-4.1-01 — Inspect passenger table and protected holder
  - **Step:** STEP-REQ-4.1-01-01
    - **Given:** passenger_manager_user has signed in with Password123! and opened My 12306 → Information management → My Passengers; the account-holder passenger is protected.
      Seed prerequisites (prepared before this scenario):
      - verified account directory: {"accounts": [{"username": "passenger_manager_user__9b2228b8b5", "email": "passenger_manager_user__9b2228b8b5@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult", "display_name": "passenger_manager_user", "holder_name": "passenger_manager_user"}], "specific_identity": {}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
      Scenario account identities: {"passenger_manager_user": "passenger_manager_user__9b2228b8b5"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Inspect passenger headers and the account-holder row.
    - **Then:** All, Name, ID type, ID number, Mobile number and Operation headers are visible; the passenger_manager_user row offers no Delete action.
    - **References:** `\ref[requirement](REQ-3.1.2)`, `\ref[image](IMG-USER-CENTER)`, `\ref[image](IMG-MY-PASSENGERS)`

### REQ-4.2 Add and validate frequent passenger

Clicking "Add new passengers"(role=button) below My Passengers opens "Add new passengers"(role=dialog). Users complete "Nationality"(role=combobox), "Name"(role=textbox), "Passport number"(role=textbox), "Passport expiration date"(role=textbox), "Date of birth"(role=textbox), "Gender"(role=group), "Email address"(role=textbox), "Mobile number"(role=textbox), and "Passenger type"(role=combobox) with Adult and Child choices. "Cancel"(role=button) abandons entry; "Determine"(role=button) with valid values adds a persistent passenger and shows Passenger added successfully. Passport P20269996 is initially unused. Missing required values show Please fill in all required fields.; a duplicate passport shows Passport number already exists.; malformed email shows Invalid email address format.; malformed mobile shows Invalid mobile number format. Rejections retain the form and add no passenger. Additional scenario passengers and current orders are UI-created rather than preseeded.

Passenger names and passport identities in records are independently identifiable visible text.

Passenger names and passport identities are independently identifiable visible text in their records. Extra passengers are created through My Passengers and Add new passengers; they are distinct from the protected account-holder passenger.

**IMG-ADD-PASSENGER · passengers**

![IMG-ADD-PASSENGER · passengers](reference/add-passenger.png)

**Type:** ATOMIC
**Dependencies:** REQ-4.1

**Scenarios:**

- SCN-REQ-4.2-01 — Add passenger with durable identity
  - **Step:** STEP-REQ-4.2-01-01
    - **Given:** passenger_manager_user has signed in with Password123! and opened My 12306 → Information management → My Passengers; the account-holder passenger is protected. Passport P20269996 is unused.
      Seed prerequisites (prepared before this scenario):
      - verified account directory: {"accounts": [{"username": "passenger_manager_user__437d22ac41", "email": "passenger_manager_user__437d22ac41@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult", "display_name": "passenger_manager_user", "holder_name": "passenger_manager_user"}], "specific_identity": {}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
      Scenario account identities: {"passenger_manager_user": "passenger_manager_user__437d22ac41"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Click Add new passengers; enter Added Passenger, P20269996, China, expiration 2028-12-31, birth 1999-02-20, Male, Adult, added.passenger@example.com and 13800000043, then click Determine; reload.
    - **Then:** Passenger added successfully. appears; exactly one P20269996 row identifies Added Passenger before and after reload.
    - **References:** `\ref[requirement](REQ-4.1)`, `\ref[image](IMG-ADD-PASSENGER)`
- SCN-REQ-4.2-02 — Reject empty passenger form
  - **Step:** STEP-REQ-4.2-02-01
    - **Given:** passenger_manager_user has signed in with Password123! and opened My 12306 → Information management → My Passengers; the account-holder passenger is protected.
      Seed prerequisites (prepared before this scenario):
      - verified account directory: {"accounts": [{"username": "passenger_manager_user__7354fa00f1", "email": "passenger_manager_user__7354fa00f1@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult", "display_name": "passenger_manager_user", "holder_name": "passenger_manager_user"}], "specific_identity": {}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
      Scenario account identities: {"passenger_manager_user": "passenger_manager_user__7354fa00f1"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Click Add new passengers, inspect its form controls and Cancel, then click Determine without entering required values.
    - **Then:** Nationality, Name, Passport number, expiration, birth, Gender, Email address, Mobile number and Passenger type are visible; Please fill in all required fields. appears and the dialog remains open.
    - **References:** `\ref[requirement](REQ-4.1)`, `\ref[image](IMG-ADD-PASSENGER)`
- SCN-REQ-4.2-03 — Reject duplicate passenger passport
  - **Step:** STEP-REQ-4.2-03-01
    - **Given:** passenger_manager_user has signed in with Password123! and opened My 12306 → Information management → My Passengers; the account-holder passenger is protected. Passenger Example has been created through Add new passengers using China, passport P20269999, expiration 2027-12-31, birth 2000-01-15, Female, Adult, passenger@example.com and 13800000040, then Determine.
      Seed prerequisites (prepared before this scenario):
      - verified account directory: {"accounts": [{"username": "passenger_manager_user__19b9a02304", "email": "passenger_manager_user__19b9a02304@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult", "display_name": "passenger_manager_user", "holder_name": "passenger_manager_user"}], "specific_identity": {}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
      Scenario account identities: {"passenger_manager_user": "passenger_manager_user__19b9a02304"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Open Add new passengers and fill Duplicate Passenger with existing passport P20269999 and otherwise valid China, expiration 2028-12-31, birth 1999-02-20, Male, Adult, added.passenger@example.com and 13800000043, then Determine.
    - **Then:** Passport number already exists. appears; the dialog stays open and no Duplicate Passenger row is added.
    - **References:** `\ref[requirement](REQ-4.1)`, `\ref[image](IMG-ADD-PASSENGER)`
- SCN-REQ-4.2-04 — Reject passenger invalid email
  - **Step:** STEP-REQ-4.2-04-01
    - **Given:** passenger_manager_user has signed in with Password123! and opened My 12306 → Information management → My Passengers; the account-holder passenger is protected. Passenger Example has been created through Add new passengers using China, passport P20269999, expiration 2027-12-31, birth 2000-01-15, Female, Adult, passenger@example.com and 13800000040, then Determine.
      Seed prerequisites (prepared before this scenario):
      - verified account directory: {"accounts": [{"username": "passenger_manager_user__e331852628", "email": "passenger_manager_user__e331852628@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult", "display_name": "passenger_manager_user", "holder_name": "passenger_manager_user"}], "specific_identity": {}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
      Scenario account identities: {"passenger_manager_user": "passenger_manager_user__e331852628"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Open Add new passengers and fill Invalid Email Passenger, passport P20260013, China, expiration 2028-12-31, birth 1999-02-20, Male, Adult, Email address invalid-email and Mobile number 13800000043, then Determine.
    - **Then:** Invalid email address format. appears; the dialog remains and no Invalid Email Passenger row is added.
    - **References:** `\ref[requirement](REQ-4.1)`, `\ref[image](IMG-ADD-PASSENGER)`

## REQ-5 Booking and payment

Support select train and passengers on booking form capability, validate submission and confirm or edit order capability, review payment details and live seat-lock countdown, pay order and classify upcoming trip, keep unpaid order in Uncompleted orders.

**Type:** FOLDER
**Dependencies:** None

### REQ-5.1 Select train and passengers on booking form capability

Support open selected-journey booking form, inspect the selected journey on its booking form, choose and remove booking passengers.

**Type:** FOLDER
**Dependencies:** None

#### REQ-5.1.1 Open selected-journey booking form

Log in, search G1001 and activate its Book action. Train Information identifies G1001 and the booking form provides Place order.

Train Information is a named region containing a Train Information: heading. G1001 Shanghai–Beijing on July 21 offers business-class seat ( ￥1870.0 ) 32% off 1 left, first-class seat ( ￥967.0 ) 24% off None left, second-class seat ( ￥576.0 ) 27% off None left, and standing ticket ( ￥576.0 ) 27% off Enough left. Passenger Example is created through My Passengers before entering booking, not preseeded. No service-agreement page is required.

**IMG-SEARCH-RESULT · train_results**

![IMG-SEARCH-RESULT · train_results](reference/search-result.png)

**IMG-BOOKING-1 · booking**

![IMG-BOOKING-1 · booking](reference/booking-1.png)

**Type:** ATOMIC
**Dependencies:** REQ-1.1.2, REQ-2.3.1, REQ-4.2

**Scenarios:**

- SCN-REQ-5.1.1-01 — Open selected-journey booking form
  - **Step:** STEP-REQ-5.1.1-01-01
    - **Given:** The verified bookable_user account creates its frequent passenger through the declared UI.
      Seed prerequisites (prepared before this scenario):
      - published services: {"Shanghai-Beijing": {"2026-07-21": [{"number": "G1001", "from_station": "Shanghai Hongqiao", "to_station": "Beijing South", "departure": "08:00", "arrival": "13:00", "duration": 300, "second_price": 576}, {"number": "G1002", "from_station": "Shanghai", "to_station": "Beijing", "departure": "13:00", "arrival": "19:00", "duration": 360, "second_price": 600}, {"number": "K1003", "from_station": "Shanghai", "to_station": "Beijing South", "departure": "00:30", "arrival": "15:30", "duration": 900, "second_price": 200}]}, "G1001_seats": {"business": {"price": 1870, "discount": "32% off", "available": 1}, "first": {"price": 967, "discount": "24% off", "available": 0}, "second": {"price": 576, "discount": "27% off", "available": 0}, "standing": {"price": 576, "discount": "27% off", "available": "Enough"}}, "allocation": "One independent business seat per scenario account; additional passengers and all current orders are created through the retained UI flows."}
      - verified account directory: {"accounts": [{"username": "bookable_user__ec2ffd4821", "email": "bookable_user__ec2ffd4821@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult", "display_name": "bookable_user", "holder_name": "bookable_user"}], "specific_identity": {}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
      Scenario account identities: {"bookable_user": "bookable_user__ec2ffd4821"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Log in, search G1001 and activate its Book action.
    - **Then:** Train Information identifies G1001 and the booking form provides Place order.
    - **References:** `\ref[requirement](REQ-1.1.2)`, `\ref[requirement](REQ-2.2)`, `\ref[requirement](REQ-4.2)`, `\ref[image](IMG-SEARCH-RESULT)`, `\ref[image](IMG-BOOKING-1)`

#### REQ-5.1.2 Inspect the selected journey on its booking form

An authenticated traveler clicks "Book"(role=button) for G1001. "Train Information"(role=region) preserves that train's route and date, shows the declared fares, discounts, and remaining inventory, and offers "Place order"(role=button).

**IMG-BOOKING-1 · booking**

![IMG-BOOKING-1 · booking](reference/booking-1.png)

**Type:** ATOMIC
**Dependencies:** REQ-5.1.1

**Scenarios:**

- SCN-REQ-5.1.2-01 — Inspect selected train and availability
  - **Step:** STEP-REQ-5.1.2-01-01
    - **Given:** The stated user has signed in with Password123!, created Passenger Example through the passenger UI using China, expiration 2027-12-31, birth 2000-01-15, Female, Adult, passenger@example.com and 13800000040, searched Shanghai–Beijing for 2026-07-21 and clicked Book in G1001. The account is bookable_user and Passenger Example has passport P20269997.
      Seed prerequisites (prepared before this scenario):
      - station directory: {"locations": ["Shanghai (上海)", "Beijing (北京)"]}
      - published services: {"Shanghai-Beijing": {"2026-07-21": [{"number": "G1001", "from_station": "Shanghai Hongqiao", "to_station": "Beijing South", "departure": "08:00", "arrival": "13:00", "duration": 300, "second_price": 576}, {"number": "G1002", "from_station": "Shanghai", "to_station": "Beijing", "departure": "13:00", "arrival": "19:00", "duration": 360, "second_price": 600}, {"number": "K1003", "from_station": "Shanghai", "to_station": "Beijing South", "departure": "00:30", "arrival": "15:30", "duration": 900, "second_price": 200}]}, "G1001_seats": {"business": {"price": 1870, "discount": "32% off", "available": 1}, "first": {"price": 967, "discount": "24% off", "available": 0}, "second": {"price": 576, "discount": "27% off", "available": 0}, "standing": {"price": 576, "discount": "27% off", "available": "Enough"}}, "allocation": "One independent business seat per scenario account; additional passengers and all current orders are created through the retained UI flows."}
      - verified account directory: {"accounts": [{"username": "bookable_user__ba2ce8567c", "email": "bookable_user__ba2ce8567c@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult", "display_name": "bookable_user", "holder_name": "bookable_user"}], "specific_identity": {}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
      Scenario account identities: {"bookable_user": "bookable_user__ba2ce8567c"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Inspect Train Information and Place order.
    - **Then:** Train Information: heading is visible; the region preserves G1001, Shanghai, Beijing and July 21, and displays business-class ￥1870.0/32% off/1 left, first-class ￥967.0/24% off/None left, second-class ￥576.0/27% off/None left and standing ￥576.0/27% off/Enough left; Place order is available.
    - **References:** `\ref[requirement](REQ-1.1.2)`, `\ref[requirement](REQ-2.2)`, `\ref[requirement](REQ-4.2)`, `\ref[requirement](REQ-5.1.1)`, `\ref[image](IMG-BOOKING-1)`

#### REQ-5.1.3 Choose booking passengers

Support select and configure booking passengers.

**Type:** FOLDER
**Dependencies:** None

##### REQ-5.1.3.1 Select and configure booking passengers

Selecting "Passenger Example"(role=checkbox) creates exactly one identity-preserving row in "Booking passengers"(role=table). Users configure "Ticket class"(role=combobox) and "Ticket type"(role=combobox) with Adult or Child, with scoped "Delete"(role=button) available before "Place order"(role=button). The parent capability's selection and fare rules apply.

Booking passengers has Ticket class, Ticket type, Name, ID type, ID number, Nationality and Operation columns. Ticket class offers Business-class seat, First-class seat, Second-class seat and Standing ticket; Ticket type offers Adult and Child. The row retains the selected passport, name and nationality. Delete is a visible row action; selection-removal behavior is outside scope.

**IMG-BOOKING-1 · booking**

![IMG-BOOKING-1 · booking](reference/booking-1.png)

**Type:** ATOMIC
**Dependencies:** REQ-5.1.1

**Scenarios:**

- SCN-REQ-5.1.3.1-01 — Select and configure booking passenger
  - **Step:** STEP-REQ-5.1.3.1-01-01
    - **Given:** The stated user has signed in with Password123!, created Passenger Example through the passenger UI using China, expiration 2027-12-31, birth 2000-01-15, Female, Adult, passenger@example.com and 13800000040, searched Shanghai–Beijing for 2026-07-21 and clicked Book in G1001. The account is bookable_user and Passenger Example has passport P20269997.
      Seed prerequisites (prepared before this scenario):
      - station directory: {"locations": ["Shanghai (上海)", "Beijing (北京)"]}
      - published services: {"Shanghai-Beijing": {"2026-07-21": [{"number": "G1001", "from_station": "Shanghai Hongqiao", "to_station": "Beijing South", "departure": "08:00", "arrival": "13:00", "duration": 300, "second_price": 576}, {"number": "G1002", "from_station": "Shanghai", "to_station": "Beijing", "departure": "13:00", "arrival": "19:00", "duration": 360, "second_price": 600}, {"number": "K1003", "from_station": "Shanghai", "to_station": "Beijing South", "departure": "00:30", "arrival": "15:30", "duration": 900, "second_price": 200}]}, "G1001_seats": {"business": {"price": 1870, "discount": "32% off", "available": 1}, "first": {"price": 967, "discount": "24% off", "available": 0}, "second": {"price": 576, "discount": "27% off", "available": 0}, "standing": {"price": 576, "discount": "27% off", "available": "Enough"}}, "allocation": "One independent business seat per scenario account; additional passengers and all current orders are created through the retained UI flows."}
      - verified account directory: {"accounts": [{"username": "bookable_user__e4fc0022c2", "email": "bookable_user__e4fc0022c2@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult", "display_name": "bookable_user", "holder_name": "bookable_user"}], "specific_identity": {}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
      Scenario account identities: {"bookable_user": "bookable_user__e4fc0022c2"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Check Passenger Example, then select Business-class seat in Ticket class and Adult in Ticket type within the P20269997 row.
    - **Then:** Booking passengers exposes Ticket class, Ticket type, Name, ID type, ID number, Nationality and Operation headers; exactly one P20269997 row identifies Passenger Example with both selections, scoped Delete and Place order available.
    - **References:** `\ref[requirement](REQ-1.1.2)`, `\ref[requirement](REQ-2.2)`, `\ref[requirement](REQ-4.2)`, `\ref[requirement](REQ-5.1.1)`, `\ref[requirement](REQ-5.1.2)`, `\ref[image](IMG-BOOKING-1)`

### REQ-5.2 Validate submission and confirm or edit order capability

Support open booking confirmation state, validate booking and open confirmation, confirm an order or return to edit.

**Type:** FOLDER
**Dependencies:** None

#### REQ-5.2.1 Open booking confirmation state

Submit Place order without activating Confirm. Please confirm the following information. opens with G1001, Passenger Example, Confirm, and Edit.

**IMG-BOOKING-CONFIRM · booking**

![IMG-BOOKING-CONFIRM · booking](reference/booking-confirm.png)

**Type:** ATOMIC
**Dependencies:** REQ-5.1.3.1

**Scenarios:**

- SCN-REQ-5.2.1-01 — Open booking confirmation state
  - **Step:** STEP-REQ-5.2.1-01-01
    - **Given:** The booking_submit_user account selects its passenger and available business-class seat through the UI.
      Seed prerequisites (prepared before this scenario):
      - published services: {"Shanghai-Beijing": {"2026-07-21": [{"number": "G1001", "from_station": "Shanghai Hongqiao", "to_station": "Beijing South", "departure": "08:00", "arrival": "13:00", "duration": 300, "second_price": 576}, {"number": "G1002", "from_station": "Shanghai", "to_station": "Beijing", "departure": "13:00", "arrival": "19:00", "duration": 360, "second_price": 600}, {"number": "K1003", "from_station": "Shanghai", "to_station": "Beijing South", "departure": "00:30", "arrival": "15:30", "duration": 900, "second_price": 200}]}, "G1001_seats": {"business": {"price": 1870, "discount": "32% off", "available": 1}, "first": {"price": 967, "discount": "24% off", "available": 0}, "second": {"price": 576, "discount": "27% off", "available": 0}, "standing": {"price": 576, "discount": "27% off", "available": "Enough"}}, "allocation": "One independent business seat per scenario account; additional passengers and all current orders are created through the retained UI flows."}
      - verified account directory: {"accounts": [{"username": "booking_submit_user__7f1c07ba54", "email": "booking_submit_user__7f1c07ba54@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult", "display_name": "booking_submit_user", "holder_name": "booking_submit_user"}], "specific_identity": {}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
      Scenario account identities: {"booking_submit_user": "booking_submit_user__7f1c07ba54"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Submit Place order without activating Confirm.
    - **Then:** Please confirm the following information. opens with G1001, Passenger Example, Confirm, and Edit.
    - **References:** `\ref[requirement](REQ-5.1.3.1)`, `\ref[image](IMG-BOOKING-CONFIRM)`

#### REQ-5.2.2 Validate booking and open confirmation

"Place order"(role=button) validates selected passengers and class inventory. Missing passengers and sold-out classes are rejected without confirmation; valid selection opens "Please confirm the following information."(role=dialog) with the selected train, passenger, "Confirm"(role=button), and "Edit"(role=button). Merely opening it creates no order. Available Standing ticket is valid and its selected class remains visible; only Confirm submits.

**IMG-BOOKING-1 · booking**

![IMG-BOOKING-1 · booking](reference/booking-1.png)

**Type:** ATOMIC
**Dependencies:** REQ-5.2.1

**Scenarios:**

- SCN-REQ-5.2.2-01 — Open confirmation for available seat
  - **Step:** STEP-REQ-5.2.2-01-01
    - **Given:** The stated user has signed in with Password123!, created Passenger Example through the passenger UI using China, expiration 2027-12-31, birth 2000-01-15, Female, Adult, passenger@example.com and 13800000040, searched Shanghai–Beijing for 2026-07-21 and clicked Book in G1001. The account is booking_submit_user with passport P20269998.
      Seed prerequisites (prepared before this scenario):
      - station directory: {"locations": ["Shanghai (上海)", "Beijing (北京)"]}
      - published services: {"Shanghai-Beijing": {"2026-07-21": [{"number": "G1001", "from_station": "Shanghai Hongqiao", "to_station": "Beijing South", "departure": "08:00", "arrival": "13:00", "duration": 300, "second_price": 576}, {"number": "G1002", "from_station": "Shanghai", "to_station": "Beijing", "departure": "13:00", "arrival": "19:00", "duration": 360, "second_price": 600}, {"number": "K1003", "from_station": "Shanghai", "to_station": "Beijing South", "departure": "00:30", "arrival": "15:30", "duration": 900, "second_price": 200}]}, "G1001_seats": {"business": {"price": 1870, "discount": "32% off", "available": 1}, "first": {"price": 967, "discount": "24% off", "available": 0}, "second": {"price": 576, "discount": "27% off", "available": 0}, "standing": {"price": 576, "discount": "27% off", "available": "Enough"}}, "allocation": "One independent business seat per scenario account; additional passengers and all current orders are created through the retained UI flows."}
      - verified account directory: {"accounts": [{"username": "booking_submit_user__f267665a01", "email": "booking_submit_user__f267665a01@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult", "display_name": "booking_submit_user", "holder_name": "booking_submit_user"}], "specific_identity": {}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
      Scenario account identities: {"booking_submit_user": "booking_submit_user__f267665a01"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Check Passenger Example, select Business-class seat in its row and click Place order.
    - **Then:** Please confirm the following information. (dialog) identifies G1001 and Passenger Example and exposes Confirm and Edit.
    - **References:** `\ref[requirement](REQ-5.1.3.1)`, `\ref[requirement](REQ-5.2.1)`, `\ref[image](IMG-BOOKING-1)`
- SCN-REQ-5.2.2-02 — Reject no passenger
  - **Step:** STEP-REQ-5.2.2-02-01
    - **Given:** The stated user has signed in with Password123!, created Passenger Example through the passenger UI using China, expiration 2027-12-31, birth 2000-01-15, Female, Adult, passenger@example.com and 13800000040, searched Shanghai–Beijing for 2026-07-21 and clicked Book in G1001. The account is bookable_user and Passenger Example has passport P20269997. No passenger is selected.
      Seed prerequisites (prepared before this scenario):
      - station directory: {"locations": ["Shanghai (上海)", "Beijing (北京)"]}
      - published services: {"Shanghai-Beijing": {"2026-07-21": [{"number": "G1001", "from_station": "Shanghai Hongqiao", "to_station": "Beijing South", "departure": "08:00", "arrival": "13:00", "duration": 300, "second_price": 576}, {"number": "G1002", "from_station": "Shanghai", "to_station": "Beijing", "departure": "13:00", "arrival": "19:00", "duration": 360, "second_price": 600}, {"number": "K1003", "from_station": "Shanghai", "to_station": "Beijing South", "departure": "00:30", "arrival": "15:30", "duration": 900, "second_price": 200}]}, "G1001_seats": {"business": {"price": 1870, "discount": "32% off", "available": 1}, "first": {"price": 967, "discount": "24% off", "available": 0}, "second": {"price": 576, "discount": "27% off", "available": 0}, "standing": {"price": 576, "discount": "27% off", "available": "Enough"}}, "allocation": "One independent business seat per scenario account; additional passengers and all current orders are created through the retained UI flows."}
      - verified account directory: {"accounts": [{"username": "bookable_user__b227b3ca77", "email": "bookable_user__b227b3ca77@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult", "display_name": "bookable_user", "holder_name": "bookable_user"}], "specific_identity": {}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
      Scenario account identities: {"bookable_user": "bookable_user__b227b3ca77"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Click Place order.
    - **Then:** Please select at least one passenger. appears and confirmation does not open.
    - **References:** `\ref[requirement](REQ-5.1.3.1)`, `\ref[requirement](REQ-5.2.1)`, `\ref[image](IMG-BOOKING-1)`
- SCN-REQ-5.2.2-03 — Reject unavailable ticket class
  - **Step:** STEP-REQ-5.2.2-03-01
    - **Given:** The stated user has signed in with Password123!, created Passenger Example through the passenger UI using China, expiration 2027-12-31, birth 2000-01-15, Female, Adult, passenger@example.com and 13800000040, searched Shanghai–Beijing for 2026-07-21 and clicked Book in G1001. The account is bookable_user and Passenger Example has passport P20269997. G1001 has no second-class seats.
      Seed prerequisites (prepared before this scenario):
      - station directory: {"locations": ["Shanghai (上海)", "Beijing (北京)"]}
      - published services: {"Shanghai-Beijing": {"2026-07-21": [{"number": "G1001", "from_station": "Shanghai Hongqiao", "to_station": "Beijing South", "departure": "08:00", "arrival": "13:00", "duration": 300, "second_price": 576}, {"number": "G1002", "from_station": "Shanghai", "to_station": "Beijing", "departure": "13:00", "arrival": "19:00", "duration": 360, "second_price": 600}, {"number": "K1003", "from_station": "Shanghai", "to_station": "Beijing South", "departure": "00:30", "arrival": "15:30", "duration": 900, "second_price": 200}]}, "G1001_seats": {"business": {"price": 1870, "discount": "32% off", "available": 1}, "first": {"price": 967, "discount": "24% off", "available": 0}, "second": {"price": 576, "discount": "27% off", "available": 0}, "standing": {"price": 576, "discount": "27% off", "available": "Enough"}}, "allocation": "One independent business seat per scenario account; additional passengers and all current orders are created through the retained UI flows."}
      - verified account directory: {"accounts": [{"username": "bookable_user__3ad263d181", "email": "bookable_user__3ad263d181@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult", "display_name": "bookable_user", "holder_name": "bookable_user"}], "specific_identity": {}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
      Scenario account identities: {"bookable_user": "bookable_user__3ad263d181"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Check Passenger Example, select Second-class seat in its row and click Place order.
    - **Then:** Sorry, there are no tickets available for the selected ticket class. appears and confirmation does not open.
    - **References:** `\ref[requirement](REQ-5.1.3.1)`, `\ref[requirement](REQ-5.2.1)`, `\ref[image](IMG-BOOKING-1)`

#### REQ-5.2.3 Confirm an order or return to edit

Support confirm a selected booking order, return from confirmation to edit.

**Type:** FOLDER
**Dependencies:** None

##### REQ-5.2.3.1 Confirm a selected booking order

In "Please confirm the following information."(role=dialog), "Confirm"(role=button) submits the selected train and passenger and opens payment with matching details and successful-submission feedback. "Edit"(role=button) remains the alternative editing action; the parent capability's full submission contract applies.

Confirm shows Order submitted successfully. and opens the selected G1001/Passenger Example order in Order details and Payment information. Passports for the dedicated booking owners are specified by each scenario.

**IMG-BOOKING-1 · booking**

![IMG-BOOKING-1 · booking](reference/booking-1.png)

**IMG-PAYMENT · payment**

![IMG-PAYMENT · payment](reference/payment.png)

**Type:** ATOMIC
**Dependencies:** REQ-5.2.2

**Scenarios:**

- SCN-REQ-5.2.3.1-01 — Confirm order and reach payment
  - **Step:** STEP-REQ-5.2.3.1-01-01
    - **Given:** The stated user has signed in with Password123!, created Passenger Example through the passenger UI using China, expiration 2027-12-31, birth 2000-01-15, Female, Adult, passenger@example.com and 13800000040, searched Shanghai–Beijing for 2026-07-21 and clicked Book in G1001. booking_confirm_user has selected Passenger Example/P20269991 and Business-class seat and opened confirmation through Place order.
      Seed prerequisites (prepared before this scenario):
      - station directory: {"locations": ["Shanghai (上海)", "Beijing (北京)"]}
      - published services: {"Shanghai-Beijing": {"2026-07-21": [{"number": "G1001", "from_station": "Shanghai Hongqiao", "to_station": "Beijing South", "departure": "08:00", "arrival": "13:00", "duration": 300, "second_price": 576}, {"number": "G1002", "from_station": "Shanghai", "to_station": "Beijing", "departure": "13:00", "arrival": "19:00", "duration": 360, "second_price": 600}, {"number": "K1003", "from_station": "Shanghai", "to_station": "Beijing South", "departure": "00:30", "arrival": "15:30", "duration": 900, "second_price": 200}]}, "G1001_seats": {"business": {"price": 1870, "discount": "32% off", "available": 1}, "first": {"price": 967, "discount": "24% off", "available": 0}, "second": {"price": 576, "discount": "27% off", "available": 0}, "standing": {"price": 576, "discount": "27% off", "available": "Enough"}}, "allocation": "One independent business seat per scenario account; additional passengers and all current orders are created through the retained UI flows."}
      - verified account directory: {"accounts": [{"username": "booking_confirm_user__3b5cb6c2e7", "email": "booking_confirm_user__3b5cb6c2e7@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult", "display_name": "booking_confirm_user", "holder_name": "booking_confirm_user"}], "specific_identity": {}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
      Scenario account identities: {"booking_confirm_user": "booking_confirm_user__3b5cb6c2e7"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Click Confirm within Please confirm the following information..
    - **Then:** Order submitted successfully. appears and Order details identifies the same G1001 and Passenger Example.
    - **References:** `\ref[requirement](REQ-5.1.3.1)`, `\ref[requirement](REQ-5.2.1)`, `\ref[requirement](REQ-5.2.2)`, `\ref[image](IMG-BOOKING-1)`, `\ref[image](IMG-PAYMENT)`

##### REQ-5.2.3.2 Return from confirmation to edit

In "Please confirm the following information."(role=dialog), "Edit"(role=button) closes confirmation and returns to booking rather than invoking "Confirm"(role=button). No order is submitted or added to Uncompleted orders; shared editing rules apply.

**IMG-BOOKING-1 · booking**

![IMG-BOOKING-1 · booking](reference/booking-1.png)

**IMG-TICKET-ORDERS · ticket_orders**

![IMG-TICKET-ORDERS · ticket_orders](reference/ticket-orders.png)

**Type:** ATOMIC
**Dependencies:** REQ-5.2.1

**Scenarios:**

- SCN-REQ-5.2.3.2-01 — Edit without submitting
  - **Step:** STEP-REQ-5.2.3.2-01-01
    - **Given:** The stated user has signed in with Password123!, created Passenger Example through the passenger UI using China, expiration 2027-12-31, birth 2000-01-15, Female, Adult, passenger@example.com and 13800000040, searched Shanghai–Beijing for 2026-07-21 and clicked Book in G1001. booking_edit_user has selected Passenger Example/P20269992 and Business-class seat and opened confirmation through Place order.
      Seed prerequisites (prepared before this scenario):
      - station directory: {"locations": ["Shanghai (上海)", "Beijing (北京)"]}
      - published services: {"Shanghai-Beijing": {"2026-07-21": [{"number": "G1001", "from_station": "Shanghai Hongqiao", "to_station": "Beijing South", "departure": "08:00", "arrival": "13:00", "duration": 300, "second_price": 576}, {"number": "G1002", "from_station": "Shanghai", "to_station": "Beijing", "departure": "13:00", "arrival": "19:00", "duration": 360, "second_price": 600}, {"number": "K1003", "from_station": "Shanghai", "to_station": "Beijing South", "departure": "00:30", "arrival": "15:30", "duration": 900, "second_price": 200}]}, "G1001_seats": {"business": {"price": 1870, "discount": "32% off", "available": 1}, "first": {"price": 967, "discount": "24% off", "available": 0}, "second": {"price": 576, "discount": "27% off", "available": 0}, "standing": {"price": 576, "discount": "27% off", "available": "Enough"}}, "allocation": "One independent business seat per scenario account; additional passengers and all current orders are created through the retained UI flows."}
      - verified account directory: {"accounts": [{"username": "booking_edit_user__ffcd06ee2e", "email": "booking_edit_user__ffcd06ee2e@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult", "display_name": "booking_edit_user", "holder_name": "booking_edit_user"}], "specific_identity": {}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
      Scenario account identities: {"booking_edit_user": "booking_edit_user__ffcd06ee2e"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Click Edit in confirmation, inspect the restored booking page, then open Uncompleted orders through My 12306.
    - **Then:** Confirmation closes; Train Information: and Place order return; Uncompleted orders contains no G1001 order.
    - **References:** `\ref[requirement](REQ-5.1.3.1)`, `\ref[requirement](REQ-5.2.1)`, `\ref[requirement](REQ-5.2.2)`, `\ref[image](IMG-BOOKING-1)`, `\ref[image](IMG-TICKET-ORDERS)`

### REQ-5.3 Review payment details and live seat-lock countdown

Confirmation opens payment showing Seats are locked, Time remained to complete your payment: and "Payment countdown"(role=region), whose only content is MM:SS. The countdown starts at 20:00 on confirmation, decreases with elapsed time, and never restarts on reload. "Order details"(role=region) and "Payment information"(role=region) retain the same selected train, passenger, passport, ticket class, and fare as confirmation, with Total: ￥xxxx.xx. For booking_payment_user with Password123!, the UI-selected business-class passenger yields CNY 1870.00 on the Shanghai–Beijing journey.

The seat-lock countdown uses the advancing client/server clock starting at 2026-07-21T00:00:00+08:00 in Asia/Shanghai; it is not a fixed text snapshot.

**IMG-PAYMENT · payment**

![IMG-PAYMENT · payment](reference/payment.png)

**Type:** ATOMIC
**Dependencies:** REQ-5.2.3.1

**Scenarios:**

- SCN-REQ-5.3-01 — Show consistent payment and running countdown
  - **Step:** STEP-REQ-5.3-01-01
    - **Given:** The stated user has signed in with Password123!, created Passenger Example through the passenger UI using China, expiration 2027-12-31, birth 2000-01-15, Female, Adult, passenger@example.com and 13800000040, searched Shanghai–Beijing for 2026-07-21 and clicked Book in G1001. booking_payment_user has selected Passenger Example/P20269993 and Business-class seat, clicked Place order and Confirm to create its unpaid order.
      Seed prerequisites (prepared before this scenario):
      - station directory: {"locations": ["Shanghai (上海)", "Beijing (北京)"]}
      - published services: {"Shanghai-Beijing": {"2026-07-21": [{"number": "G1001", "from_station": "Shanghai Hongqiao", "to_station": "Beijing South", "departure": "08:00", "arrival": "13:00", "duration": 300, "second_price": 576}, {"number": "G1002", "from_station": "Shanghai", "to_station": "Beijing", "departure": "13:00", "arrival": "19:00", "duration": 360, "second_price": 600}, {"number": "K1003", "from_station": "Shanghai", "to_station": "Beijing South", "departure": "00:30", "arrival": "15:30", "duration": 900, "second_price": 200}]}, "G1001_seats": {"business": {"price": 1870, "discount": "32% off", "available": 1}, "first": {"price": 967, "discount": "24% off", "available": 0}, "second": {"price": 576, "discount": "27% off", "available": 0}, "standing": {"price": 576, "discount": "27% off", "available": "Enough"}}, "allocation": "One independent business seat per scenario account; additional passengers and all current orders are created through the retained UI flows."}
      - verified account directory: {"accounts": [{"username": "booking_payment_user__c688a2b321", "email": "booking_payment_user__c688a2b321@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult", "display_name": "booking_payment_user", "holder_name": "booking_payment_user"}], "specific_identity": {}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
      Scenario account identities: {"booking_payment_user": "booking_payment_user__c688a2b321"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Inspect payment details and countdown, observe its decrease over elapsed time, record the remaining seconds and reload.
    - **Then:** The seat-lock message is visible; Order details retains G1001, Passenger Example, P20269993 and Business-class seat with Total: ￥1870.00. Payment countdown is MM:SS, initially at most 20:00 and near that start, decreases with time, and after reload does not exceed its pre-reload remaining value.
    - **References:** `\ref[requirement](REQ-5.2.3.1)`, `\ref[image](IMG-PAYMENT)`

### REQ-5.4 Pay order and classify upcoming trip

Clicking "Pay"(role=button) simulates payment and shows Payment successful. The paid G1001 is classified as upcoming before departure and appears under "Upcoming trips"(role=tab) with a visible Refund button (navigation-only; refund execution is outside scope). The booking_paid_user and booking_upcoming_user accounts, both with Password123!, establish their passengers and unpaid Shanghai–Beijing orders through UI before payment. Status and category survive reload.

The pre-provisioned verified account booking_upcoming_user has email booking_upcoming_user@example.com and password Password123!.

**IMG-PAYMENT · payment**

![IMG-PAYMENT · payment](reference/payment.png)

**IMG-TICKET-ORDERS · ticket_orders**

![IMG-TICKET-ORDERS · ticket_orders](reference/ticket-orders.png)

**Type:** ATOMIC
**Dependencies:** REQ-5.3, REQ-3.2.1

**Scenarios:**

- SCN-REQ-5.4-01 — Pay and persist upcoming state
  - **Step:** STEP-REQ-5.4-01-01
    - **Given:** The stated user has signed in with Password123!, created Passenger Example through the passenger UI using China, expiration 2027-12-31, birth 2000-01-15, Female, Adult, passenger@example.com and 13800000040, searched Shanghai–Beijing for 2026-07-21 and clicked Book in G1001. booking_paid_user has selected Passenger Example/P20269995 and Business-class seat and confirmed an unpaid G1001 order.
      Seed prerequisites (prepared before this scenario):
      - station directory: {"locations": ["Shanghai (上海)", "Beijing (北京)"]}
      - published services: {"Shanghai-Beijing": {"2026-07-21": [{"number": "G1001", "from_station": "Shanghai Hongqiao", "to_station": "Beijing South", "departure": "08:00", "arrival": "13:00", "duration": 300, "second_price": 576}, {"number": "G1002", "from_station": "Shanghai", "to_station": "Beijing", "departure": "13:00", "arrival": "19:00", "duration": 360, "second_price": 600}, {"number": "K1003", "from_station": "Shanghai", "to_station": "Beijing South", "departure": "00:30", "arrival": "15:30", "duration": 900, "second_price": 200}]}, "G1001_seats": {"business": {"price": 1870, "discount": "32% off", "available": 1}, "first": {"price": 967, "discount": "24% off", "available": 0}, "second": {"price": 576, "discount": "27% off", "available": 0}, "standing": {"price": 576, "discount": "27% off", "available": "Enough"}}, "allocation": "One independent business seat per scenario account; additional passengers and all current orders are created through the retained UI flows."}
      - verified account directory: {"accounts": [{"username": "booking_paid_user__ee27938bcc", "email": "booking_paid_user__ee27938bcc@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult", "display_name": "booking_paid_user", "holder_name": "booking_paid_user"}], "specific_identity": {}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
      Scenario account identities: {"booking_paid_user": "booking_paid_user__ee27938bcc"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Click Pay, open Upcoming trips through My 12306 → Order center → Ticket orders, then reload.
    - **Then:** Payment successful. appears; G1001 displays Paid with Refund available in Upcoming trips and remains Paid after reload.
    - **References:** `\ref[requirement](REQ-5.2.3.1)`, `\ref[image](IMG-PAYMENT)`, `\ref[image](IMG-TICKET-ORDERS)`

### REQ-5.5 Keep unpaid order in Uncompleted orders

When booking_unpaid_user with Password123! confirms its UI-created Shanghai–Beijing order but does not pay, the unpaid order appears in "Uncompleted orders"(role=tab) with "Pay"(role=button). Status and classification persist after reload; unpaid orders do not appear in Upcoming trips.

**IMG-PAYMENT · payment**

![IMG-PAYMENT · payment](reference/payment.png)

**IMG-TICKET-ORDERS · ticket_orders**

![IMG-TICKET-ORDERS · ticket_orders](reference/ticket-orders.png)

**Type:** ATOMIC
**Dependencies:** REQ-5.2.3.1, REQ-3.2.1

**Scenarios:**

- SCN-REQ-5.5-01 — Persist unpaid order category
  - **Step:** STEP-REQ-5.5-01-01
    - **Given:** The stated user has signed in with Password123!, created Passenger Example through the passenger UI using China, expiration 2027-12-31, birth 2000-01-15, Female, Adult, passenger@example.com and 13800000040, searched Shanghai–Beijing for 2026-07-21 and clicked Book in G1001. booking_unpaid_user has selected Passenger Example/P20269990 and Business-class seat and confirmed an order without paying.
      Seed prerequisites (prepared before this scenario):
      - station directory: {"locations": ["Shanghai (上海)", "Beijing (北京)"]}
      - published services: {"Shanghai-Beijing": {"2026-07-21": [{"number": "G1001", "from_station": "Shanghai Hongqiao", "to_station": "Beijing South", "departure": "08:00", "arrival": "13:00", "duration": 300, "second_price": 576}, {"number": "G1002", "from_station": "Shanghai", "to_station": "Beijing", "departure": "13:00", "arrival": "19:00", "duration": 360, "second_price": 600}, {"number": "K1003", "from_station": "Shanghai", "to_station": "Beijing South", "departure": "00:30", "arrival": "15:30", "duration": 900, "second_price": 200}]}, "G1001_seats": {"business": {"price": 1870, "discount": "32% off", "available": 1}, "first": {"price": 967, "discount": "24% off", "available": 0}, "second": {"price": 576, "discount": "27% off", "available": 0}, "standing": {"price": 576, "discount": "27% off", "available": "Enough"}}, "allocation": "One independent business seat per scenario account; additional passengers and all current orders are created through the retained UI flows."}
      - verified account directory: {"accounts": [{"username": "booking_unpaid_user__c217ceeb2c", "email": "booking_unpaid_user__c217ceeb2c@example.com", "password": "Password123!", "verified": true, "gender": "Male", "passenger_type": "Adult", "display_name": "booking_unpaid_user", "holder_name": "booking_unpaid_user"}], "specific_identity": {}, "other_identity": "Each other account has a distinct unused passport assigned by evaluator; use source username as holder name, nationality China, ID type Foreign passport. Holder automatically appears as nondeletable frequent passenger. No other frequent passengers/current orders initially."}
      Scenario account identities: {"booking_unpaid_user": "booking_unpaid_user__c217ceeb2c"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Open Uncompleted orders, inspect the order and reload, then select Upcoming trips.
    - **Then:** G1001 is Unpaid with Pay available in Uncompleted orders, remains Unpaid after reload, and is absent from Upcoming trips.
    - **References:** `\ref[requirement](REQ-5.2.3.1)`, `\ref[image](IMG-PAYMENT)`, `\ref[image](IMG-TICKET-ORDERS)`
