# BookStack knowledge base

A knowledge base for organizing and reading shelves, books, chapters, and pages.

Dates and time-dependent content use UTC and the shared application/evaluator clock 2026-10-06T12:00:00Z.

For session and personal dashboard state: Established through login, opening content, favoriting content, or saving pages/drafts. No private storage injection.

## REQ-1 Application entry and navigation

The logged-out homepage provides search input and links to Login, Shelves and Books. These entry points are available throughout the content flows. Visual layout follows the supplied references; search behavior is not specified by this source.

Content metadata and personal preferences persist across navigation and reload.

**Type:** FOLDER
**Dependencies:** None

### REQ-1.1 Open the application

Opening the application homepage at / while logged out displays "Login"(role=link), "Shelves"(role=link), and "Books"(role=link) as its public entry points.

The logged-out homepage also provides a search input; search behavior is not specified. Login, Shelves, and Books entry points remain available throughout the content flows.

**IMG-INDEX · home**

![IMG-INDEX · home](reference/index.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-1.1-01 — Show logged-out navigation
  - **Step:** STEP-REQ-1.1-01-01
    - **Given:** A fresh anonymous browser opens the initialized knowledge base; verified account and bootstrap shelf exist, but no session has been established.
    - **When:** Open / and inspect the homepage entry links.
    - **Then:** The homepage displays visible Login, Shelves and Books links with their declared accessible names.
    - **References:** `\ref[image](IMG-INDEX)`

### REQ-1.2 Return home

Opening / from the shelves list returns to the homepage, which exposes "Login"(role=link), "Shelves"(role=link), and "Books"(role=link).

**IMG-SHELVES · shelves**

![IMG-SHELVES · shelves](reference/shelves.png)

**IMG-INDEX · home**

![IMG-INDEX · home](reference/index.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-1.2-01 — Return from shelves
  - **Step:** STEP-REQ-1.2-01-01
    - **Given:** The anonymous homepage is open and the seeded Benchmark Bootstrap Shelf is available in Shelf list.
      Seed prerequisites (prepared before this scenario):
      - bootstrap shelf: {"name": "Benchmark Bootstrap Shelf", "description": "Entry shelf for the New Shelf creation action.", "tags": [], "books": []}
    - **When:** Click Shelves, verify Shelf list opens, then open / to return to the homepage.
    - **Then:** The homepage returns with its Books link visible.
    - **References:** `\ref[requirement](REQ-4.1)`, `\ref[image](IMG-SHELVES)`, `\ref[image](IMG-INDEX)`

## REQ-2 Account access

A preverified account can log in; account registration is outside scope. Content browsing and the source-described content mutations remain available while logged out; drafts and personal lists require login.

For verified account: Registration and verification are outside scope; the scenarios use the existing verified account described below.

**Type:** FOLDER
**Dependencies:** None

### REQ-2.1 Open login

Clicking "Login"(role=link) in navigation opens a login form containing "Email"(role=textbox), "Password"(role=textbox), an initially unchecked "Remember Me"(role=checkbox), and a Login submit action.

Registration is outside scope. Content browsing and the declared content mutations remain available while logged out; drafts and personal lists require login.

**IMG-INDEX · home**

![IMG-INDEX · home](reference/index.png)

**IMG-LOGIN · login**

![IMG-LOGIN · login](reference/login.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-2.1-01 — Show login form
  - **Step:** STEP-REQ-2.1-01-01
    - **Given:** A fresh browser is on the anonymous application entry with Login available on the page.
    - **When:** Click the Login navigation link and inspect the displayed form.
    - **Then:** Email and Password fields and the Login submit button are visible; Remember Me is present and unchecked.
    - **References:** `\ref[requirement](REQ-1.1)`, `\ref[image](IMG-INDEX)`, `\ref[image](IMG-LOGIN)`

### REQ-2.2 Authenticate verified account

Users enter a verified account's credentials in "Email"(role=textbox) and "Password"(role=textbox), select "Remember Me"(role=checkbox), and submit the form reached through "Login"(role=link). Successful authentication returns to the homepage, shows BookStack User in the top-right user area, and enables the personal dashboard lists. Invalid-credential wording is unspecified.

**IMG-INDEX-AFTER-LOGIN · home**

![IMG-INDEX-AFTER-LOGIN · home](reference/index_after_login.png)

**IMG-LOGIN · login**

![IMG-LOGIN · login](reference/login.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-2.2-01 — Log in with remember me
  - **Step:** STEP-REQ-2.2-01-01
    - **Given:** verified account contains verified bookstack_user@example.com with Password123! and nickname BookStack User; the browser is anonymous on the application entry.
      Seed prerequisites (prepared before this scenario):
      - verified account: {"nickname": "BookStack User", "email": "bookstack_user@example.com", "password": "Password123!"}
    - **When:** Click Login on the page, fill Email and Password with those credentials, check Remember Me, and click the Login submit button.
    - **Then:** The homepage visibly displays BookStack User and My Recent Drafts, confirming authentication and access to the personal dashboard. No unprovided remember-me expiry guarantee is inferred.
    - **References:** `\ref[requirement](REQ-2.1)`, `\ref[image](IMG-INDEX-AFTER-LOGIN)`, `\ref[image](IMG-LOGIN)`

## REQ-3 Authenticated dashboard

The authenticated homepage shows recent drafts, recently viewed items, most viewed favorites, recently updated pages, recent activity and dashboard controls as visually referenced.

**Type:** FOLDER
**Dependencies:** None

### REQ-3.1 View authenticated dashboard

Successful login displays an authenticated dashboard with "My Recent Drafts"(role=region), "My Recently Viewed"(role=region), "My Most Viewed Favorites"(role=region), and "Recently Updated Pages"(role=region), each containing its corresponding personal or content list. Recent activity and dashboard controls also follow the visual reference.

Dates and time-dependent content use UTC and the shared clock 2026-10-06T12:00:00Z.

**IMG-LOGIN · login**

![IMG-LOGIN · login](reference/login.png)

**IMG-INDEX-AFTER-LOGIN · home**

![IMG-INDEX-AFTER-LOGIN · home](reference/index_after_login.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-3.1-01 — Show personal dashboard regions
  - **Step:** STEP-REQ-3.1-01-01
    - **Given:** The verified verified account exists and a fresh anonymous browser is at the application entry.
      Seed prerequisites (prepared before this scenario):
      - verified account: {"nickname": "BookStack User", "email": "bookstack_user@example.com", "password": "Password123!"}
    - **When:** Open Login, fill Email with bookstack_user@example.com and Password with Password123!, check Remember Me, and submit Login.
    - **Then:** The authenticated homepage displays My Recent Drafts, My Recently Viewed, My Most Viewed Favorites and Recently Updated Pages as named regions.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-LOGIN)`, `\ref[image](IMG-INDEX-AFTER-LOGIN)`

## REQ-4 Organize shelves

Shelves contain a name, description, related books and tags. Support browsing, creation, editing, cancellation and confirmed deletion. Related-book editing remains part of the requirement even where not sampled by a test.

For bootstrap shelf: Source only exposes New Shelf from an existing shelf. One immutable bootstrap shelf breaks that creation prerequisite; other shelves are UI-created.

**Type:** FOLDER
**Dependencies:** None

### REQ-4.1 Browse shelfs

Activating "Shelves"(role=link) on the page displays "Shelf list"(role=region). Each shelf appears exactly once as a keyboard-accessible "{item name}"(role=button) identified by its business name; a semantically equivalent link is also permitted. No total list size is prescribed.

**IMG-INDEX · home**

![IMG-INDEX · home](reference/index.png)

**IMG-SHELVES · shelves**

![IMG-SHELVES · shelves](reference/shelves.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-4.1-01 — Show a uniquely identified item
  - **Step:** STEP-REQ-4.1-01-01
    - **Given:** As an anonymous visitor, create a case-isolated Shelf 4.1 through the bootstrap shelf's New Shelf form, using Reference shelf description. and knowledge-base, docs as metadata.
      Seed prerequisites (prepared before this scenario):
      - bootstrap shelf: {"name": "Benchmark Bootstrap Shelf", "description": "Entry shelf for the New Shelf creation action.", "tags": [], "books": []}
    - **When:** Click Shelves on the page and inspect Shelf list for the full isolated name.
    - **Then:** The created shelf's opening entry appears exactly once and is visible and keyboard-accessible within Shelf list.
    - **References:** `\ref[requirement](REQ-4.3)`, `\ref[image](IMG-INDEX)`, `\ref[image](IMG-SHELVES)`

### REQ-4.2 Open shelf details

Choosing "{item name}"(role=button) in "Shelf list"(role=region), or the allowed equivalent link, opens that shelf's details with a heading bearing its name and information belonging to the selected shelf. Its included books and related actions are available from these details.

**IMG-SHELVES · shelves**

![IMG-SHELVES · shelves](reference/shelves.png)

**IMG-SHELF · shelf**

![IMG-SHELF · shelf](reference/shelf.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-4.2-01 — Open from global list
  - **Step:** STEP-REQ-4.2-01-01
    - **Given:** An anonymous visitor has UI-created isolated Shelf 4.2.1 with Reference shelf description. and knowledge-base, docs.
      Seed prerequisites (prepared before this scenario):
      - bootstrap shelf: {"name": "Benchmark Bootstrap Shelf", "description": "Entry shelf for the New Shelf creation action.", "tags": [], "books": []}
    - **When:** Click Shelves, then activate that exact shelf's entry within Shelf list.
    - **Then:** The selected shelf's detail heading matches its full isolated name and its saved description is visible; a different shelf is not opened.
    - **References:** `\ref[requirement](REQ-4.1)`, `\ref[image](IMG-SHELVES)`, `\ref[image](IMG-SHELF)`

### REQ-4.3 Create or abandon shelf

While logged out, users open the bootstrap shelf through Shelves and Shelf list, then click "New Shelf"(role=button) to enter "Name"(role=textbox), "Description"(role=textbox), and "Tags"(role=textbox). "Save Shelf"(role=button) creates exactly one shelf with that metadata and returns to Shelf list; the metadata persists across navigation and reload. "Cancel"(role=button) instead returns to Shelfs without creating the entered object. Runtime names may append the evaluator's run, worker, and case identity to source examples.

The existing Benchmark Bootstrap Shelf has description Entry shelf for the New Shelf creation action., no tags and no books. It remains an immutable entry shelf for New Shelf; shelves created by the user are separate objects.

**IMG-SHELVES · shelves**

![IMG-SHELVES · shelves](reference/shelves.png)

**IMG-SHELF · shelf**

![IMG-SHELF · shelf](reference/shelf.png)

**IMG-CREATE-SHELF · shelf_form**

![IMG-CREATE-SHELF · shelf_form](reference/create_shelf.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-4.3-01 — Save a new shelf
  - **Step:** STEP-REQ-4.3-01-01
    - **Given:** The anonymous application has bootstrap shelf and no shelf with the isolated Shelf Created 4.3.1 name.
      Seed prerequisites (prepared before this scenario):
      - bootstrap shelf: {"name": "Benchmark Bootstrap Shelf", "description": "Entry shelf for the New Shelf creation action.", "tags": [], "books": []}
    - **When:** Open Shelves, select Benchmark Bootstrap Shelf, click New Shelf, enter the isolated name in Name, Shelf created by corresponding prerequisite behavior. in Description and created, shelf in Tags, then click Save Shelf. Open the saved shelf, reload and reopen Edit.
    - **Then:** Saving returns to Shelf list with exactly one visible entry. The saved name, description and tags remain in the reopened metadata form after reload, demonstrating persistence of the entered metadata.
    - **References:** `\ref[requirement](REQ-1.1)`, `\ref[image](IMG-SHELVES)`, `\ref[image](IMG-SHELF)`, `\ref[image](IMG-CREATE-SHELF)`
- SCN-REQ-4.3-02 — Cancel new shelf
  - **Step:** STEP-REQ-4.3-02-01
    - **Given:** The anonymous browser has opened Benchmark Bootstrap Shelf through Shelves and Shelf list; the isolated Shelf Cancelled 4.3.2 does not exist.
      Seed prerequisites (prepared before this scenario):
      - bootstrap shelf: {"name": "Benchmark Bootstrap Shelf", "description": "Entry shelf for the New Shelf creation action.", "tags": [], "books": []}
    - **When:** Click New Shelf, fill Name with the isolated title, Description with Unsaved shelf description 4.3.2. and Tags with cancelled, shelf, then click Cancel.
    - **Then:** Shelfs list returns, with no entry for the unsaved name; none of the entered metadata creates a shelf.
    - **References:** `\ref[requirement](REQ-1.1)`, `\ref[image](IMG-SHELVES)`, `\ref[image](IMG-SHELF)`, `\ref[image](IMG-CREATE-SHELF)`

### REQ-4.5 Edit or abandon shelf metadata

On the selected shelf's details, "Edit"(role=button) opens "Name"(role=textbox), "Description"(role=textbox), and "Tags"(role=textbox) prefilled with saved values. "Save Shelf"(role=button) updates that same shelf and returns to its details with the updated heading and description; changes survive reload. "Cancel"(role=button) discards all pending changes and returns to the unchanged details. Related-book editing is also supported.

**IMG-SHELF · shelf**

![IMG-SHELF · shelf](reference/shelf.png)

**IMG-EDIT-SHELVE · shelf_form**

![IMG-EDIT-SHELVE · shelf_form](reference/edit_shelve.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-4.5-01 — Save metadata changes
  - **Step:** STEP-REQ-4.5-01-01
    - **Given:** UI-created isolated Shelf 4.5.1 has Reference shelf description. and knowledge-base, docs; its details are open anonymously.
      Seed prerequisites (prepared before this scenario):
      - bootstrap shelf: {"name": "Benchmark Bootstrap Shelf", "description": "Entry shelf for the New Shelf creation action.", "tags": [], "books": []}
    - **When:** Click Edit and verify Name, Description and Tags are prefilled. Replace Name with isolated Shelf Updated 4.5.1 and Description with Shelf updated by corresponding prerequisite behavior., retain the tags, and click Save Shelf. Reload the returned details and reopen Edit.
    - **Then:** The updated heading and description are visible before and after reload. The reopened fields retain the updated name, description and tags on that same shelf.
    - **References:** `\ref[requirement](REQ-4.2)`, `\ref[image](IMG-SHELF)`, `\ref[image](IMG-EDIT-SHELVE)`
- SCN-REQ-4.5-02 — Cancel metadata changes
  - **Step:** STEP-REQ-4.5-02-01
    - **Given:** UI-created isolated Shelf 4.5.2 has Reference shelf description. and knowledge-base, docs; its details are open anonymously.
      Seed prerequisites (prepared before this scenario):
      - bootstrap shelf: {"name": "Benchmark Bootstrap Shelf", "description": "Entry shelf for the New Shelf creation action.", "tags": [], "books": []}
    - **When:** Click Edit, replace Name with isolated Shelf Updated 4.5.2 and Description with Shelf updated by corresponding prerequisite behavior., then click Cancel.
    - **Then:** Details return with the original heading and description and no heading for the replacement name; pending metadata was not committed.
    - **References:** `\ref[requirement](REQ-4.2)`, `\ref[image](IMG-SHELF)`, `\ref[image](IMG-EDIT-SHELVE)`

### REQ-4.4 Delete or retain shelf

Clicking "Delete"(role=button) on a selected shelf opens confirmation. "Confirm Delete"(role=button) removes that shelf and returns to Shelfs, where its entry is absent from "Shelf list"(role=region); the deletion remains effective across navigation. "Cancel"(role=button) keeps the shelf and preserves its original heading and description.

**IMG-DELETE-SHELVES · shelf**

![IMG-DELETE-SHELVES · shelf](reference/delete_shelves.png)

**IMG-SHELVES · shelves**

![IMG-SHELVES · shelves](reference/shelves.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-4.4-01 — Confirm deletion
  - **Step:** STEP-REQ-4.4-01-01
    - **Given:** An anonymous visitor has UI-created isolated Shelf 4.4.1 with Reference shelf description. and is viewing that shelf's details.
      Seed prerequisites (prepared before this scenario):
      - bootstrap shelf: {"name": "Benchmark Bootstrap Shelf", "description": "Entry shelf for the New Shelf creation action.", "tags": [], "books": []}
    - **When:** Click Delete, inspect confirmation with Confirm Delete and Cancel, then click Confirm Delete; reopen Shelves after reload.
    - **Then:** Shelfs list returns and contains no entry for the deleted shelf before or after reload.
    - **References:** `\ref[requirement](REQ-4.2)`, `\ref[image](IMG-DELETE-SHELVES)`, `\ref[image](IMG-SHELVES)`
- SCN-REQ-4.4-02 — Cancel deletion
  - **Step:** STEP-REQ-4.4-02-01
    - **Given:** An anonymous visitor has UI-created isolated Shelf 4.4.2 with Reference shelf description. and is viewing its details.
      Seed prerequisites (prepared before this scenario):
      - bootstrap shelf: {"name": "Benchmark Bootstrap Shelf", "description": "Entry shelf for the New Shelf creation action.", "tags": [], "books": []}
    - **When:** Click Delete and then Cancel in the confirmation.
    - **Then:** The same shelf details remain, with the original heading and Reference shelf description.; the shelf is not deleted.
    - **References:** `\ref[requirement](REQ-4.2)`, `\ref[image](IMG-DELETE-SHELVES)`, `\ref[image](IMG-SHELVES)`

## REQ-5 Manage books

Books contain a name, rich-text description, optional cover image, tags, default page template, chapters and pages. Support creation from the global list and from a shelf, metadata editing and confirmed deletion. Optional cover and default-template behavior are retained but not sampled; the source gives no format or template catalog rules.

**Type:** FOLDER
**Dependencies:** None

### REQ-5.1 Browse books

Clicking "Books"(role=link) on the page displays "Book list"(role=region). Each book appears exactly once as a keyboard-accessible "{item name}"(role=button) identified by its business name, with an equivalent link also allowed. No total list size is prescribed.

**IMG-INDEX · home**

![IMG-INDEX · home](reference/index.png)

**IMG-BOOKS · books**

![IMG-BOOKS · books](reference/books.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-5.1-01 — Show a uniquely identified item
  - **Step:** STEP-REQ-5.1-01-01
    - **Given:** An anonymous visitor has UI-created isolated Book 5.1 with Reference book description. and manual, handbook through Books, Create New Book, metadata fields and Save Book.
    - **When:** Click Books on the page and inspect Book list.
    - **Then:** Exactly one visible keyboard-accessible opening entry identifies that full isolated book name.
    - **References:** `\ref[requirement](REQ-5.3)`, `\ref[image](IMG-INDEX)`, `\ref[image](IMG-BOOKS)`

### REQ-5.2 Open book details

Selecting "{item name}"(role=button), or its allowed equivalent link, in "Book list"(role=region) opens the corresponding book's details with its name as the heading and information belonging to that book. The same selection behavior is available from the Book list on its containing shelf.

**IMG-BOOKS · books**

![IMG-BOOKS · books](reference/books.png)

**IMG-SHELF · shelf**

![IMG-SHELF · shelf](reference/shelf.png)

**IMG-BOOK · book**

![IMG-BOOK · book](reference/book.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-5.2-01 — Open from global list
  - **Step:** STEP-REQ-5.2-01-01
    - **Given:** An anonymous visitor has UI-created isolated Book 5.2.1 with Reference book description. and manual, handbook.
    - **When:** Click Books, then activate the exact book entry in Book list.
    - **Then:** The opened detail heading is that book's name and its saved description is visible.
    - **References:** `\ref[requirement](REQ-5.1)`, `\ref[image](IMG-BOOKS)`, `\ref[image](IMG-SHELF)`, `\ref[image](IMG-BOOK)`
- SCN-REQ-5.2-02 — Open from containing shelf
  - **Step:** STEP-REQ-5.2-02-01
    - **Given:** Through UI, create isolated Shelf 5.2.2 and then Book 5.2.2 from that shelf's Create New Book form, associating the two objects.
      Seed prerequisites (prepared before this scenario):
      - bootstrap shelf: {"name": "Benchmark Bootstrap Shelf", "description": "Entry shelf for the New Shelf creation action.", "tags": [], "books": []}
    - **When:** Follow the containing shelf's named parent entry, then choose the isolated book from that shelf's Book list.
    - **Then:** The selected book detail heading matches its name and the shelf-created description is visible, preserving the parent association.
    - **References:** `\ref[requirement](REQ-5.6)`, `\ref[image](IMG-BOOKS)`, `\ref[image](IMG-SHELF)`, `\ref[image](IMG-BOOK)`

### REQ-5.3 Create or abandon book

While logged out, users open Books and click "Create New Book"(role=button), then enter "Name"(role=textbox), "Description"(role=textbox), and "Tags"(role=textbox). "Save Book"(role=button) creates one book with that metadata and opens its details with the saved name and description. Description supports rich text, a cover is optional, and a default page template can be chosen. "Cancel"(role=button) returns to Books without creating the entered book. Saved metadata survives navigation and reload; runtime names may append evaluator run, worker, and case identity to source examples.

The source specifies no cover-image format or default-template catalog rules.

**IMG-BOOKS · books**

![IMG-BOOKS · books](reference/books.png)

**IMG-CREATE-BOOK · book_form**

![IMG-CREATE-BOOK · book_form](reference/create_book.png)

**IMG-BOOK · book**

![IMG-BOOK · book](reference/book.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-5.3-01 — Save a new book
  - **Step:** STEP-REQ-5.3-01-01
    - **Given:** The browser is anonymous and no book has the isolated Book Created 5.3.1 name.
    - **When:** Click Books and Create New Book, fill Name with the isolated title, Description with Book created by corresponding prerequisite behavior. and Tags with created, book, then Save Book. Reload details and reopen Edit.
    - **Then:** Saving opens the new book's heading and description. Reopened Name, Description and Tags retain all submitted metadata after reload.
    - **References:** `\ref[requirement](REQ-1.1)`, `\ref[image](IMG-BOOKS)`, `\ref[image](IMG-CREATE-BOOK)`, `\ref[image](IMG-BOOK)`
- SCN-REQ-5.3-02 — Cancel new book
  - **Step:** STEP-REQ-5.3-02-01
    - **Given:** The anonymous Books list is open and isolated Book Cancelled 5.3.2 does not exist.
    - **When:** Click Create New Book, enter the isolated name, Unsaved book description 5.3.2. and cancelled, book in the metadata fields, then click Cancel.
    - **Then:** Books list returns with no entry for that name; the unsaved book is not created.
    - **References:** `\ref[requirement](REQ-1.1)`, `\ref[image](IMG-BOOKS)`, `\ref[image](IMG-CREATE-BOOK)`, `\ref[image](IMG-BOOK)`

### REQ-5.4 Edit or abandon book metadata

On the selected book's details, "Edit"(role=button) opens "Name"(role=textbox), "Description"(role=textbox), and "Tags"(role=textbox) prefilled with their saved values. "Save Book"(role=button) changes that same book and returns to its details with the updated heading and description, persisting after reload. "Cancel"(role=button) returns to the unchanged details and discards all pending edits.

Book metadata editing also retains the rich-text description, optional cover image and selected default page template. Cover format and the template catalog are unspecified; saving or cancelling follows the same persistence rules as the other metadata.

**IMG-BOOK · book**

![IMG-BOOK · book](reference/book.png)

**IMG-EDIT-BOOK · book_form**

![IMG-EDIT-BOOK · book_form](reference/edit_book.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-5.4-01 — Save metadata changes
  - **Step:** STEP-REQ-5.4-01-01
    - **Given:** UI-created isolated Book 5.4.1 has Reference book description. and manual, handbook, and its details are open anonymously.
    - **When:** Click Edit and check the prefilled metadata, replace Name with isolated Book Updated 5.4.1 and Description with Book updated by corresponding prerequisite behavior., retain tags and Save Book; reload and reopen Edit.
    - **Then:** The new heading and description appear before and after reload; the reopened metadata fields contain the saved replacement values and retained tags.
    - **References:** `\ref[requirement](REQ-5.2)`, `\ref[image](IMG-BOOK)`, `\ref[image](IMG-EDIT-BOOK)`
- SCN-REQ-5.4-02 — Cancel metadata changes
  - **Step:** STEP-REQ-5.4-02-01
    - **Given:** UI-created isolated Book 5.4.2 has Reference book description. and manual, handbook, and its detail is open anonymously.
    - **When:** Click Edit, enter isolated Book Updated 5.4.2 and Book updated by corresponding prerequisite behavior. as replacement name and description, then Cancel.
    - **Then:** The original heading and description return, and no heading has the proposed replacement name.
    - **References:** `\ref[requirement](REQ-5.2)`, `\ref[image](IMG-BOOK)`, `\ref[image](IMG-EDIT-BOOK)`

### REQ-5.5 Delete or retain book

Clicking "Delete"(role=button) on the selected book opens confirmation. "Confirm Delete"(role=button) removes that book and returns to Books, with its entry absent from "Book list"(role=region) across subsequent navigation. "Cancel"(role=button) keeps the book's original heading and description unchanged.

**IMG-DELETE-BOOK · book**

![IMG-DELETE-BOOK · book](reference/delete_book.png)

**IMG-BOOKS · books**

![IMG-BOOKS · books](reference/books.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-5.5-01 — Confirm deletion
  - **Step:** STEP-REQ-5.5-01-01
    - **Given:** UI-created isolated Book 5.5.1 with Reference book description. is open anonymously.
    - **When:** Click Delete, inspect Confirm Delete and Cancel, click Confirm Delete, then reload and reopen Books.
    - **Then:** Books list contains no entry for the selected book both immediately and after reload.
    - **References:** `\ref[requirement](REQ-5.2)`, `\ref[image](IMG-DELETE-BOOK)`, `\ref[image](IMG-BOOKS)`
- SCN-REQ-5.5-02 — Cancel deletion
  - **Step:** STEP-REQ-5.5-02-01
    - **Given:** UI-created isolated Book 5.5.2 with Reference book description. is open anonymously.
    - **When:** Click Delete and Cancel in confirmation.
    - **Then:** The original book heading and Reference book description. remain visible; no deletion is committed.
    - **References:** `\ref[requirement](REQ-5.2)`, `\ref[image](IMG-DELETE-BOOK)`, `\ref[image](IMG-BOOKS)`

### REQ-5.6 Create a book in a shelf

Clicking "Create New Book"(role=button) on a shelf's details opens a creation form with "Name"(role=textbox), "Description"(role=textbox), and "Tags"(role=textbox). "Save Book"(role=button) creates the book under that specific shelf and opens its details with its name and a "{containing shelf name}"(role=button) parent action, for which an equivalent link is also permitted. Following the parent action opens the containing shelf, whose "Book list"(role=region) includes the created book.

**IMG-SHELF · shelf**

![IMG-SHELF · shelf](reference/shelf.png)

**IMG-CREATE-BOOK · book_form**

![IMG-CREATE-BOOK · book_form](reference/create_book.png)

**IMG-BOOK · book**

![IMG-BOOK · book](reference/book.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-5.6-01 — Save a book with shelf association
  - **Step:** STEP-REQ-5.6-01-01
    - **Given:** An anonymous visitor has UI-created isolated Shelf 5.6.1 and is viewing it; isolated Book Created 5.6.1 does not exist.
      Seed prerequisites (prepared before this scenario):
      - bootstrap shelf: {"name": "Benchmark Bootstrap Shelf", "description": "Entry shelf for the New Shelf creation action.", "tags": [], "books": []}
    - **When:** Click the shelf's Create New Book, fill Name with the isolated book name, Description with Book created by corresponding prerequisite behavior. and Tags with created, shelf-book, then Save Book. Follow the named containing shelf entry.
    - **Then:** The new book detail shows its name; its parent entry opens the correct shelf, whose Book list exposes the created book exactly once.
    - **References:** `\ref[requirement](REQ-4.2)`, `\ref[requirement](REQ-5.3)`, `\ref[image](IMG-SHELF)`, `\ref[image](IMG-CREATE-BOOK)`, `\ref[image](IMG-BOOK)`

## REQ-6 Author and read content

Pages are reading units, chapters organize pages. Support published pages, user-owned drafts, draft deletion, chapter creation and entry, and reading pages from book or chapter page lists.

**Type:** FOLDER
**Dependencies:** None

### REQ-6.1 Publish or save a draft page

Clicking "New Page"(role=button) on a book opens "Page title"(role=textbox) and "Write your page content here..."(role=textbox). "Save Page"(role=button) publishes the entered title and body, returns to the book, and adds exactly one entry to "Page list"(role=region), including while logged out. When authenticated, users can instead click "Save Draft"(role=button) to save an owned draft, which appears exactly once in the homepage's "My Recent Drafts"(role=region). Saved drafts can be reopened from the parent book's Page list to resume editing or delete them. REQ-2.2 is required only for the Save Draft branch.

Dates and time-dependent content use UTC and the shared clock 2026-10-06T12:00:00Z.

Published pages can be organized under a chapter belonging to their parent book. Saving keeps the book/chapter association so that the page is readable from the appropriate chapter Page list as well as its book context. Drafts belong to the authenticated author and their parent book.

**IMG-BOOK · book**

![IMG-BOOK · book](reference/book.png)

**IMG-PAGE-DRAFT · page_editor**

![IMG-PAGE-DRAFT · page_editor](reference/page_draft.png)

**IMG-INDEX-AFTER-LOGIN · home**

![IMG-INDEX-AFTER-LOGIN · home](reference/index_after_login.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-6.1-01 — Publish a page
  - **Step:** STEP-REQ-6.1-01-01
    - **Given:** An anonymous visitor has UI-created isolated Book 6.1.1 and is viewing it; isolated Page Created 6.1.1 does not exist.
    - **When:** Click New Page, fill Page title with the isolated name and Write your page content here... with Page content created by corresponding prerequisite behavior., then Save Page.
    - **Then:** The parent book returns with exactly one visible Page list entry for the saved page, without requiring login.
    - **References:** `\ref[requirement](REQ-5.3)`, `\ref[image](IMG-BOOK)`, `\ref[image](IMG-PAGE-DRAFT)`, `\ref[image](IMG-INDEX-AFTER-LOGIN)`
- SCN-REQ-6.1-02 — Save an owned recent draft
  - **Step:** STEP-REQ-6.1-02-01
    - **Given:** Log in through Email and Password as verified account, create isolated Book 6.1.2 through UI, and open that book.
      Seed prerequisites (prepared before this scenario):
      - verified account: {"nickname": "BookStack User", "email": "bookstack_user@example.com", "password": "Password123!"}
    - **When:** Click New Page, enter isolated Page Draft 6.1.2 and Draft content created by corresponding prerequisite behavior., then Save Draft. Open the parent book if the editor remains and open / to return home.
    - **Then:** The parent Page list contains exactly one draft entry; the authenticated My Recent Drafts region also contains that draft exactly once.
    - **References:** `\ref[requirement](REQ-5.3)`, `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-BOOK)`, `\ref[image](IMG-PAGE-DRAFT)`, `\ref[image](IMG-INDEX-AFTER-LOGIN)`

### REQ-6.2 Delete an owned draft

Opening an owned draft while logged in offers "Delete Draft"(role=button). Clicking it opens confirmation with "Confirm Delete"(role=button); confirming returns to the parent book and removes that draft from "Page list"(role=region).

**IMG-BOOKS · books**

![IMG-BOOKS · books](reference/books.png)

**IMG-BOOK · book**

![IMG-BOOK · book](reference/book.png)

**IMG-DELETE-DRAFT · page_editor**

![IMG-DELETE-DRAFT · page_editor](reference/delete_draft.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-6.2-01 — Confirm draft deletion
  - **Step:** STEP-REQ-6.2-01-01
    - **Given:** verified account is authenticated and owns a UI-created isolated Draft 6.1.3 with Disposable draft. under isolated Book 6.1.3, established through New Page and Save Draft.
      Seed prerequisites (prepared before this scenario):
      - verified account: {"nickname": "BookStack User", "email": "bookstack_user@example.com", "password": "Password123!"}
    - **When:** Open Books, select the parent, select the draft in Page list, click Delete Draft and Confirm Delete.
    - **Then:** The parent book's heading returns and Page list contains no entry for that draft.
    - **References:** `\ref[requirement](REQ-6.1)`, `\ref[image](IMG-BOOKS)`, `\ref[image](IMG-BOOK)`, `\ref[image](IMG-DELETE-DRAFT)`

### REQ-6.3 Create and enter a chapter

Clicking "New Chapter"(role=button) on a book opens "Name"(role=textbox) and "Description"(role=textbox). "Save Chapter"(role=button) saves the entered chapter and adds exactly one entry to "Chapter list"(role=region). Opening its "{chapter name}"(role=button) entry displays that chapter's heading and saved description.

A chapter belongs to its selected book, organizes pages and exposes its own Page list containing pages associated with that chapter. It must not display pages belonging only to another chapter or book.

**IMG-BOOK · book**

![IMG-BOOK · book](reference/book.png)

**IMG-CREATE-CHAPTER · create_chapter**

![IMG-CREATE-CHAPTER · create_chapter](reference/create_chapter.png)

**IMG-CHAPTER · chapter**

![IMG-CHAPTER · chapter](reference/chapter.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-6.3-01 — Save and open a chapter
  - **Step:** STEP-REQ-6.3-01-01
    - **Given:** An anonymous visitor has UI-created isolated Book 6.2.1 and is viewing it; isolated Chapter Created 6.2.1 does not exist.
    - **When:** Click New Chapter, enter the isolated name and Chapter created by corresponding prerequisite behavior. in Name and Description, then Save Chapter. Click that chapter's entry in Chapter list.
    - **Then:** Saving adds exactly one Chapter list entry. Selecting it opens the same chapter's heading and saved description.
    - **References:** `\ref[requirement](REQ-5.3)`, `\ref[image](IMG-BOOK)`, `\ref[image](IMG-CREATE-CHAPTER)`, `\ref[image](IMG-CHAPTER)`

### REQ-6.4 Read a page or reopen its editor

Selecting "{page title}"(role=button) from a book or chapter's "Page list"(role=region) displays the published page's title heading and saved body. "Edit"(role=button) on the reading page opens an editor prefilled with the current title in "Page title"(role=textbox) and body in "Write your page content here..."(role=textbox), with "Save Page"(role=button) available to save the page.

**IMG-BOOK · book**

![IMG-BOOK · book](reference/book.png)

**IMG-CHAPTER · chapter**

![IMG-CHAPTER · chapter](reference/chapter.png)

**IMG-PAGE · page**

![IMG-PAGE · page](reference/page.png)

**IMG-PAGE-DRAFT · page_editor**

![IMG-PAGE-DRAFT · page_editor](reference/page_draft.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-6.4-01 — Read selected page
  - **Step:** STEP-REQ-6.4-01-01
    - **Given:** An anonymous visitor has UI-published isolated Page 6.3.1 with Reading content for Page 6.3.1. under isolated Book 6.3.1; the parent Page list is open.
    - **When:** Activate the exact page entry in Page list.
    - **Then:** The page heading matches the isolated title and its saved body is visible.
    - **References:** `\ref[requirement](REQ-6.1)`, `\ref[image](IMG-BOOK)`, `\ref[image](IMG-CHAPTER)`, `\ref[image](IMG-PAGE)`, `\ref[image](IMG-PAGE-DRAFT)`
- SCN-REQ-6.4-02 — Reopen page editor
  - **Step:** STEP-REQ-6.4-02-01
    - **Given:** An anonymous visitor has UI-published isolated Page 6.3.2 with Reading content for Page 6.3.2. under isolated Book 6.3.2.
    - **When:** Open that page from Page list and click Edit.
    - **Then:** The editor's Page title and Write your page content here... fields contain the saved title and body, and Save Page is visible.
    - **References:** `\ref[requirement](REQ-6.1)`, `\ref[image](IMG-BOOK)`, `\ref[image](IMG-CHAPTER)`, `\ref[image](IMG-PAGE)`, `\ref[image](IMG-PAGE-DRAFT)`

## REQ-7 Recently viewed content

Authenticated visits to shelves, books, chapters and pages are recorded for that user. My Recently Viewed contains at most ten records and opens the selected item. The source does not define a tie-breaker or eviction order.

**Type:** FOLDER
**Dependencies:** None

### REQ-7.1 Record and reopen viewed content

Authenticated visits to shelves, books, chapters, and pages record those items for the user. Opening / returns home, where "My Recently Viewed"(role=region) contains at most ten records and one entry per visited identity. Selecting "{visited item name}"(role=button), or the allowed equivalent link, opens the corresponding item.

The source does not define a tie-breaker or eviction order for recently viewed records.

Dates and time-dependent content use UTC and the shared clock 2026-10-06T12:00:00Z.

**IMG-SHELVES · shelves**

![IMG-SHELVES · shelves](reference/shelves.png)

**IMG-SHELF · shelf**

![IMG-SHELF · shelf](reference/shelf.png)

**IMG-BOOKS · books**

![IMG-BOOKS · books](reference/books.png)

**IMG-BOOK · book**

![IMG-BOOK · book](reference/book.png)

**IMG-CHAPTER · chapter**

![IMG-CHAPTER · chapter](reference/chapter.png)

**IMG-PAGE · page**

![IMG-PAGE · page](reference/page.png)

**IMG-INDEX-AFTER-LOGIN · home**

![IMG-INDEX-AFTER-LOGIN · home](reference/index_after_login.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-7.1-01 — Record shelf visit
  - **Step:** STEP-REQ-7.1-01-01
    - **Given:** verified account is authenticated and isolated Shelf 7.1 has been created through the public shelf form.
      Seed prerequisites (prepared before this scenario):
      - verified account: {"nickname": "BookStack User", "email": "bookstack_user@example.com", "password": "Password123!"}
      - bootstrap shelf: {"name": "Benchmark Bootstrap Shelf", "description": "Entry shelf for the New Shelf creation action.", "tags": [], "books": []}
    - **When:** Open the exact shelf from Shelves and Shelf list, then open / to return home.
    - **Then:** My Recently Viewed contains exactly one entry for that visited shelf, with the region containing no more than ten records.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[requirement](REQ-4.2)`, `\ref[image](IMG-SHELVES)`, `\ref[image](IMG-SHELF)`, `\ref[image](IMG-BOOKS)`, `\ref[image](IMG-BOOK)`, `\ref[image](IMG-CHAPTER)`, `\ref[image](IMG-PAGE)`, `\ref[image](IMG-INDEX-AFTER-LOGIN)`
- SCN-REQ-7.1-02 — Reopen visited shelf
  - **Step:** STEP-REQ-7.1-02-01
    - **Given:** verified account is authenticated and isolated Shelf 7.2 has been UI-created and visited through Shelf list.
      Seed prerequisites (prepared before this scenario):
      - verified account: {"nickname": "BookStack User", "email": "bookstack_user@example.com", "password": "Password123!"}
      - bootstrap shelf: {"name": "Benchmark Bootstrap Shelf", "description": "Entry shelf for the New Shelf creation action.", "tags": [], "books": []}
    - **When:** Open / to return home and click that shelf's exact entry in My Recently Viewed.
    - **Then:** The recent list exposes the identity exactly once and selecting it opens that same shelf's heading.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[requirement](REQ-4.2)`, `\ref[image](IMG-SHELVES)`, `\ref[image](IMG-SHELF)`, `\ref[image](IMG-BOOKS)`, `\ref[image](IMG-BOOK)`, `\ref[image](IMG-CHAPTER)`, `\ref[image](IMG-PAGE)`, `\ref[image](IMG-INDEX-AFTER-LOGIN)`

## REQ-8 Personal favorites

Authenticated users can favorite and unfavorite shelves, books, chapters and pages. My Most Viewed Favorites contains at most four items, and a dedicated favorites page exposes the complete collection. Ranking ties and the name of the complete-list entry are not specified; these are not tested.

**Type:** FOLDER
**Dependencies:** None

### REQ-8.1 Favorite and unfavorite content

On an authenticated shelf, book, chapter, or page details view, "Favorite"(role=button) initially exposes aria-pressed=false. Clicking it stores a personal favorite and changes the action to "Unfavorite"(role=button) with aria-pressed=true. Clicking Unfavorite removes the preference and restores Favorite with aria-pressed=false. The selected state persists after reload and follows the same behavior for all four content types.

Favorites and unfavorites are scoped to the authenticated user; another account does not acquire the same personal preference. Saved preferences remain consistent across navigation as well as reload.

**IMG-BOOK · book**

![IMG-BOOK · book](reference/book.png)

**IMG-FAVOURITES · favourites**

![IMG-FAVOURITES · favourites](reference/favourites.png)

**IMG-INDEX · home**

![IMG-INDEX · home](reference/index.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-8.1-01 — Favorite a book
  - **Step:** STEP-REQ-8.1-01-01
    - **Given:** verified account is authenticated and is viewing UI-created isolated Book 8.1; Favorite starts with pressed=false.
      Seed prerequisites (prepared before this scenario):
      - verified account: {"nickname": "BookStack User", "email": "bookstack_user@example.com", "password": "Password123!"}
    - **When:** Click Favorite on that book's details.
    - **Then:** The action changes to Unfavorite and reports pressed=true for that book.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[requirement](REQ-5.3)`, `\ref[image](IMG-BOOK)`, `\ref[image](IMG-FAVOURITES)`, `\ref[image](IMG-INDEX)`
- SCN-REQ-8.1-02 — Persist removal of a favorite
  - **Step:** STEP-REQ-8.1-02-01
    - **Given:** verified account is authenticated and has UI-created isolated Book Unfavorite; it has not yet been favorited.
      Seed prerequisites (prepared before this scenario):
      - verified account: {"nickname": "BookStack User", "email": "bookstack_user@example.com", "password": "Password123!"}
    - **When:** Click Favorite, reload, click Unfavorite, reload again, and open / to return home.
    - **Then:** After the first reload Unfavorite still reports pressed=true; after removal Favorite reports pressed=false before and after reload. My Most Viewed Favorites has no entry for the removed book.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[requirement](REQ-5.3)`, `\ref[image](IMG-BOOK)`, `\ref[image](IMG-FAVOURITES)`, `\ref[image](IMG-INDEX)`

### REQ-8.2 Open a homepage favorite

After an item is favorited, the authenticated homepage's "My Most Viewed Favorites"(role=region) exposes that item as "{favorite item name}"(role=button), with an equivalent link also permitted. The region contains at most four items; selecting an entry opens the corresponding item. A dedicated favorites page exposes the complete collection.

Ranking ties and the name of the complete favorites collection entry are unspecified.

**IMG-INDEX-AFTER-LOGIN · home**

![IMG-INDEX-AFTER-LOGIN · home](reference/index_after_login.png)

**IMG-FAVOURITES · favourites**

![IMG-FAVOURITES · favourites](reference/favourites.png)

**IMG-BOOK · book**

![IMG-BOOK · book](reference/book.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-8.2-01 — Open favorited book
  - **Step:** STEP-REQ-8.2-01-01
    - **Given:** verified account is authenticated and has UI-created isolated Book 8.2, then clicked Favorite and observed Unfavorite with pressed=true.
      Seed prerequisites (prepared before this scenario):
      - verified account: {"nickname": "BookStack User", "email": "bookstack_user@example.com", "password": "Password123!"}
    - **When:** Open /, inspect My Most Viewed Favorites and activate the exact isolated book entry there.
    - **Then:** The favorite entry appears once in a list of no more than four items and opens the same book's heading.
    - **References:** `\ref[requirement](REQ-8.1)`, `\ref[image](IMG-INDEX-AFTER-LOGIN)`, `\ref[image](IMG-FAVOURITES)`, `\ref[image](IMG-BOOK)`

## REQ-9 Recently updated pages

The homepage shows at most five recently created or edited pages and opens a selected page. The source does not define ranking tie-breakers.

**Type:** FOLDER
**Dependencies:** None

### REQ-9.1 Open a recently updated page

Creating or editing a page updates "Recently Updated Pages"(role=region) on the homepage. This region contains at most five items, and selecting "{page title}"(role=button), or the permitted equivalent link, opens that page with its saved title and body.

Ranking tie-breakers are unspecified.

Dates and time-dependent content use UTC and the shared clock 2026-10-06T12:00:00Z.

**IMG-INDEX · home**

![IMG-INDEX · home](reference/index.png)

**IMG-PAGE · page**

![IMG-PAGE · page](reference/page.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-9.1-01 — Open recently published page
  - **Step:** STEP-REQ-9.1-01-01
    - **Given:** An anonymous visitor has UI-created isolated Book 9.1 and published isolated Page Updated 9.1 with Page content created by corresponding prerequisite behavior.
    - **When:** Open / and select that page's exact entry in Recently Updated Pages.
    - **Then:** The list has no more than five entries and includes the new page once; selection opens its saved heading and body.
    - **References:** `\ref[requirement](REQ-6.1)`, `\ref[image](IMG-INDEX)`, `\ref[image](IMG-PAGE)`
