# BookStack knowledge base

A knowledge base for organizing and reading books and pages.

Dates and time-dependent content use UTC and the shared application/evaluator clock 2026-10-06T12:00:00Z.

## REQ-1 Application entry and navigation

Support open the book workspace.

**Type:** FOLDER
**Dependencies:** None

### REQ-1.1 Open the book workspace

Opening / displays a public book workspace with a Books link in navigation. Books remains available throughout book and page flows. The workspace requires no authentication; books and published pages are created through UI and persist across navigation and reload.

**IMG-INDEX · home**

![IMG-INDEX · home](reference/index.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-1.1-01 — Open the book workspace
  - **Step:** STEP-REQ-1.1-01-01
    - **Given:** A fresh anonymous browser opens the initialized public book workspace. No account or shelf is required.
    - **When:** Open / and inspect the Books navigation link.
    - **Then:** Books is visible and opens the book workspace.
    - **References:** `\ref[image](IMG-INDEX)`

## REQ-2 Manage books

Support browse books, open book details, create or abandon book, edit or abandon book metadata, delete or retain book.

**Type:** FOLDER
**Dependencies:** None

### REQ-2.1 Browse books

Clicking "Books"(role=link) on the page displays "Book list"(role=region). Each book appears exactly once as a keyboard-accessible "{item name}"(role=button) identified by its business name, with an equivalent link also allowed. No total list size is prescribed.

**IMG-INDEX · home**

![IMG-INDEX · home](reference/index.png)

**IMG-BOOKS · books**

![IMG-BOOKS · books](reference/books.png)

**Type:** ATOMIC
**Dependencies:** REQ-1.1, REQ-2.3

**Scenarios:**

- SCN-REQ-2.1-01 — Show a uniquely identified item
  - **Step:** STEP-REQ-2.1-01-01
    - **Given:** An anonymous visitor has UI-created isolated Book 5.1 with Reference book description. and manual, handbook through Books, Create New Book, metadata fields and Save Book.
    - **When:** Click Books on the page and inspect Book list.
    - **Then:** Exactly one visible keyboard-accessible opening entry identifies that full isolated book name.
    - **References:** `\ref[requirement](REQ-2.3)`, `\ref[image](IMG-INDEX)`, `\ref[image](IMG-BOOKS)`

### REQ-2.2 Open book details

Selecting the exact book name in Book list opens that book, showing its saved name as a heading and its description. Each book entry is uniquely identified by business name; either a button or a link is allowed.

**IMG-BOOKS · books**

![IMG-BOOKS · books](reference/books.png)

**IMG-BOOK · book**

![IMG-BOOK · book](reference/book.png)

**Type:** ATOMIC
**Dependencies:** REQ-1.1, REQ-2.3

**Scenarios:**

- SCN-REQ-2.2-01 — Open from global list
  - **Step:** STEP-REQ-2.2-01-01
    - **Given:** An anonymous visitor has UI-created isolated Book 5.2.1 with Reference book description. and manual, handbook.
    - **When:** Click Books, then activate the exact book entry in Book list.
    - **Then:** The opened detail heading is that book's name and its saved description is visible.
    - **References:** `\ref[requirement](REQ-2.1)`, `\ref[image](IMG-BOOKS)`, `\ref[image](IMG-BOOK)`

### REQ-2.3 Create or abandon book

From Books, Create New Book opens Name, Description and Tags text fields. Save Book creates exactly one book, opens its saved name heading and description, and persists metadata across reload. Cancel returns to Books without creating the pending book. All these flows are available without login; test names append run, worker and case identity.

**IMG-BOOKS · books**

![IMG-BOOKS · books](reference/books.png)

**IMG-CREATE-BOOK · book_form**

![IMG-CREATE-BOOK · book_form](reference/create_book.png)

**IMG-BOOK · book**

![IMG-BOOK · book](reference/book.png)

**Type:** ATOMIC
**Dependencies:** REQ-1.1

**Scenarios:**

- SCN-REQ-2.3-01 — Save a new book
  - **Step:** STEP-REQ-2.3-01-01
    - **Given:** The browser is anonymous and no book has the isolated Book Created 5.3.1 name.
    - **When:** Click Books and Create New Book, fill Name with the isolated title, Description with Book created by corresponding prerequisite behavior. and Tags with created, book, then Save Book. Reload details and reopen Edit.
    - **Then:** Saving opens the new book's heading and description. Reopened Name, Description and Tags retain all submitted metadata after reload.
    - **References:** `\ref[requirement](REQ-1.1)`, `\ref[image](IMG-BOOKS)`, `\ref[image](IMG-CREATE-BOOK)`, `\ref[image](IMG-BOOK)`
- SCN-REQ-2.3-02 — Cancel new book
  - **Step:** STEP-REQ-2.3-02-01
    - **Given:** The anonymous Books list is open and isolated Book Cancelled 5.3.2 does not exist.
    - **When:** Click Create New Book, enter the isolated name, Unsaved book description 5.3.2. and cancelled, book in the metadata fields, then click Cancel.
    - **Then:** Books list returns with no entry for that name; the unsaved book is not created.
    - **References:** `\ref[requirement](REQ-1.1)`, `\ref[image](IMG-BOOKS)`, `\ref[image](IMG-CREATE-BOOK)`, `\ref[image](IMG-BOOK)`

### REQ-2.4 Edit or abandon book metadata

Edit on the selected book opens Name, Description and Tags prefilled from that book. Save Book updates the same book and returns to its updated heading and description, persisting after reload. Cancel discards pending changes and returns to the unchanged book.

**IMG-BOOK · book**

![IMG-BOOK · book](reference/book.png)

**IMG-EDIT-BOOK · book_form**

![IMG-EDIT-BOOK · book_form](reference/edit_book.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.2

**Scenarios:**

- SCN-REQ-2.4-01 — Save metadata changes
  - **Step:** STEP-REQ-2.4-01-01
    - **Given:** UI-created isolated Book 5.4.1 has Reference book description. and manual, handbook, and its details are open anonymously.
    - **When:** Click Edit and check the prefilled metadata, replace Name with isolated Book Updated 5.4.1 and Description with Book updated by corresponding prerequisite behavior., retain tags and Save Book; reload and reopen Edit.
    - **Then:** The new heading and description appear before and after reload; the reopened metadata fields contain the saved replacement values and retained tags.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-BOOK)`, `\ref[image](IMG-EDIT-BOOK)`
- SCN-REQ-2.4-02 — Cancel metadata changes
  - **Step:** STEP-REQ-2.4-02-01
    - **Given:** UI-created isolated Book 5.4.2 has Reference book description. and manual, handbook, and its detail is open anonymously.
    - **When:** Click Edit, enter isolated Book Updated 5.4.2 and Book updated by corresponding prerequisite behavior. as replacement name and description, then Cancel.
    - **Then:** The original heading and description return, and no heading has the proposed replacement name.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-BOOK)`, `\ref[image](IMG-EDIT-BOOK)`

### REQ-2.5 Delete or retain book

Clicking "Delete"(role=button) on the selected book opens confirmation. "Confirm Delete"(role=button) removes that book and returns to Books, with its entry absent from "Book list"(role=region) across subsequent navigation. "Cancel"(role=button) keeps the book's original heading and description unchanged.

**IMG-DELETE-BOOK · book**

![IMG-DELETE-BOOK · book](reference/delete_book.png)

**IMG-BOOKS · books**

![IMG-BOOKS · books](reference/books.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.2

**Scenarios:**

- SCN-REQ-2.5-01 — Confirm deletion
  - **Step:** STEP-REQ-2.5-01-01
    - **Given:** UI-created isolated Book 5.5.1 with Reference book description. is open anonymously.
    - **When:** Click Delete, inspect Confirm Delete and Cancel, click Confirm Delete, then reload and reopen Books.
    - **Then:** Books list contains no entry for the selected book both immediately and after reload.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-DELETE-BOOK)`, `\ref[image](IMG-BOOKS)`
- SCN-REQ-2.5-02 — Cancel deletion
  - **Step:** STEP-REQ-2.5-02-01
    - **Given:** UI-created isolated Book 5.5.2 with Reference book description. is open anonymously.
    - **When:** Click Delete and Cancel in confirmation.
    - **Then:** The original book heading and Reference book description. remain visible; no deletion is committed.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-DELETE-BOOK)`, `\ref[image](IMG-BOOKS)`

## REQ-3 Author and read content

Support publish a page in a book, read a page or reopen its editor.

**Type:** FOLDER
**Dependencies:** None

### REQ-3.1 Publish a page in a book

New Page on a book opens the Page title and Write your page content here... textboxes (also exposed with those placeholders). Save Page publishes title and body, returns to the parent book and adds exactly one entry to Page list (region). This is available without login. Page entries are uniquely identified by title, using a button or link. Saving retains the book association and persists across navigation and reload.

**IMG-BOOK · book**

![IMG-BOOK · book](reference/book.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.2

**Scenarios:**

- SCN-REQ-3.1-01 — Publish a page
  - **Step:** STEP-REQ-3.1-01-01
    - **Given:** An anonymous visitor has UI-created isolated Book 6.1.1 and is viewing it; isolated Page Created 6.1.1 does not exist.
    - **When:** Click New Page, fill Page title with the isolated name and Write your page content here... with Page content created by corresponding prerequisite behavior., then Save Page.
    - **Then:** The parent book returns with exactly one visible Page list entry for the saved page, without requiring login.
    - **References:** `\ref[requirement](REQ-2.3)`, `\ref[image](IMG-BOOK)`

### REQ-3.2 Read a page or reopen its editor

Selecting the exact page title from a book's Page list opens its saved title heading and body. Edit opens an editor prefilled in Page title and Write your page content here..., with Save Page available. All page reading and editing flows are public.

**IMG-BOOK · book**

![IMG-BOOK · book](reference/book.png)

**IMG-PAGE · page**

![IMG-PAGE · page](reference/page.png)

**Type:** ATOMIC
**Dependencies:** REQ-3.1

**Scenarios:**

- SCN-REQ-3.2-01 — Read selected page
  - **Step:** STEP-REQ-3.2-01-01
    - **Given:** An anonymous visitor has UI-published isolated Page 6.3.1 with Reading content for Page 6.3.1. under isolated Book 6.3.1; the parent Page list is open.
    - **When:** Activate the exact page entry in Page list.
    - **Then:** The page heading matches the isolated title and its saved body is visible.
    - **References:** `\ref[requirement](REQ-3.1)`, `\ref[image](IMG-BOOK)`, `\ref[image](IMG-PAGE)`
- SCN-REQ-3.2-02 — Reopen page editor
  - **Step:** STEP-REQ-3.2-02-01
    - **Given:** An anonymous visitor has UI-published isolated Page 6.3.2 with Reading content for Page 6.3.2. under isolated Book 6.3.2.
    - **When:** Open that page from Page list and click Edit.
    - **Then:** The editor's Page title and Write your page content here... fields contain the saved title and body, and Save Page is visible.
    - **References:** `\ref[requirement](REQ-3.1)`, `\ref[image](IMG-BOOK)`, `\ref[image](IMG-PAGE)`
