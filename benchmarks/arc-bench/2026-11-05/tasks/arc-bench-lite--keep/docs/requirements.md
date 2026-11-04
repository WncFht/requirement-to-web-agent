# Keep personal note management

A personal note management application for creating, editing, pinning, and archiving notes.

The interface uses en-US. Tested note states are established through normal user actions in a single application instance. No fixed benchmark clock or historical deleted-note seed data is required.

## REQ-1 Workspace navigation

Support open the personal workspace.

**Type:** FOLDER
**Dependencies:** None

### REQ-1.1 Open the personal workspace

Opening / displays a personal notes workspace in en-US with a visible Sidebar navigation, Notes and Archived buttons, and Take a note. Notes is initially selected with aria-current=true. The sidebar starts expanded and Toggle sidebar reports aria-expanded=true; collapse/expand behavior is outside scope. No authentication is required. Notes and Archived show their respective persisted collections. Additional controls visible in reference screenshots are optional unless declared in a retained requirement.

**IMG-HOME-PAGE · notes**

![IMG-HOME-PAGE · notes](reference/home_page.png)

**IMG-SIDEBAR · notes**

![IMG-SIDEBAR · notes](reference/sidebar.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-1.1-01 — Open the workspace
  - **Step:** STEP-REQ-1.1-01-01
    - **Given:** A fresh browser opens the personal workspace without authentication; Sidebar starts expanded with Notes selected.
      Seed prerequisites (prepared before this scenario):
      - default label: {"name": "Reminders", "icon": "distinct reminder icon"}
    - **When:** Open / and inspect Sidebar, Notes, Archived, Toggle sidebar and Take a note.
    - **Then:** Sidebar, Notes, Archived and Take a note are visible; Toggle sidebar reports expanded=true and Notes reports current=true.
    - **References:** `\ref[image](IMG-HOME-PAGE)`, `\ref[image](IMG-SIDEBAR)`

## REQ-2 Manage the note lifecycle

Support list pinned and regular notes separately, create and autosave a personal note, edit and persist note content, archive notes and restore them to active Notes, pin and unpin notes.

**Type:** FOLDER
**Dependencies:** None

### REQ-2.1 List pinned and regular notes separately

Notes contains exactly one Pinned notes region and one Other notes region. Each active note appears exactly once in its correct section as a region whose accessible name is its full visible title. Archived notes are excluded from both sections. Note title is the business identity; actions revealed on hover remain keyboard accessible and are scoped to that note. Buttons, fields and regions retain their declared accessible names.

**IMG-HOME-PAGE · notes**

![IMG-HOME-PAGE · notes](reference/home_page.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.2, REQ-2.5

**Scenarios:**

- SCN-REQ-2.1-01 — Separate pinned and regular notes
  - **Step:** STEP-REQ-2.1-01-01
    - **Given:** Notes is open. Through Take a note, Title, Content and Close, create a case-isolated Sprint goals note with Finish the sprint and Pin note selected, and a regular Groceries note with Milk and bread.
    - **When:** Inspect the "Pinned notes"(role=region) and "Other notes"(role=region) collections using each note's full isolated title.
    - **Then:** Each collection exists once. Sprint goals appears exactly once only in Pinned notes and Groceries exactly once only in Other notes; neither note is duplicated across sections and each remains visible with its saved content.
    - **References:** `\ref[requirement](REQ-2.5)`, `\ref[image](IMG-HOME-PAGE)`

### REQ-2.2 Create and autosave a personal note

Take a note opens Note editor (dialog), with Title and Content textboxes and Close (button). Close automatically saves exactly one active note with the entered title and multiline content, without a Save action. The note survives reload. Pin note in the editor supports the retained pinning behavior; colors and labels are outside scope. Nonempty titles may include run, worker and case suffixes; empty-input rules are unspecified.

**IMG-CREATE-NOTE-HOME-PAGE · notes**

![IMG-CREATE-NOTE-HOME-PAGE · notes](reference/create_note_home_page.png)

**IMG-CREATE-NOTE-FORM · notes**

![IMG-CREATE-NOTE-FORM · notes](reference/create_note_form.png)

**Type:** ATOMIC
**Dependencies:** REQ-1.1

**Scenarios:**

- SCN-REQ-2.2-01 — Autosave on closing the editor
  - **Step:** STEP-REQ-2.2-01-01
    - **Given:** The personal Notes workspace is open and the case-isolated New note title does not yet exist.
    - **When:** Click "Take a note"(role=button); in "Note editor"(role=dialog), fill Title with the isolated New note name and Content with First line followed by a newline and Second line, then click Close without using any Save action.
    - **Then:** Note editor closes and exactly one visible note region with that title displays the entered title and both content lines.
    - **References:** `\ref[requirement](REQ-1.1)`, `\ref[image](IMG-CREATE-NOTE-HOME-PAGE)`, `\ref[image](IMG-CREATE-NOTE-FORM)`
- SCN-REQ-2.2-02 — Keep a created note after reload
  - **Step:** STEP-REQ-2.2-02-01
    - **Given:** Notes is open and no note uses the case-isolated Persistent note title.
    - **When:** Open Note editor through Take a note, enter the isolated Persistent note title and Saved personal content, click Close, and reload the page.
    - **Then:** The editor closes on save; after reload exactly one visible note region retains that title and Saved personal content.
    - **References:** `\ref[requirement](REQ-1.1)`, `\ref[image](IMG-CREATE-NOTE-HOME-PAGE)`, `\ref[image](IMG-CREATE-NOTE-FORM)`

### REQ-2.3 Edit and persist note content

Clicking "Open {title}"(role=button) on a particular note opens Note editor with that note's existing title and content. Changing Content and closing the editor saves the replacement content on the same note without changing its title or creating a duplicate. The updated content remains visible after reload.

Note actions revealed on hover remain keyboard-accessible. Actions are buttons except menu choices, which are menuitems; fields have associated accessible names. Note actions are scoped to the note region identified by its visible title.

**IMG-NOTE-EDITING · notes**

![IMG-NOTE-EDITING · notes](reference/note_editing.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.2

**Scenarios:**

- SCN-REQ-2.3-01 — Save an edited note
  - **Step:** STEP-REQ-2.3-01-01
    - **Given:** Notes contains a UI-created case-isolated Project ideas note with Initial editable content, created through Take a note, Title, Content and Close.
    - **When:** Click "Open {title}"(role=button) within that note; verify Title and Content are prefilled, replace Content with Updated editable content, click Close, and reload.
    - **Then:** The editor initially contains the saved title and content, then closes. After reload exactly one note retains the original title and replacement content, with no Initial editable content in that note.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-NOTE-EDITING)`

### REQ-2.4 Archive notes and restore them to active Notes

Clicking "Archive {title}"(role=button) moves the selected active note out of Notes into "Archived notes"(role=region) and displays "Note archived"(role=status) with "Undo"(role=button). Undo restores the same note and content to Notes, removes it from the archive, and shows Action undone. Clicking "Archived"(role=button) displays archived notes separately from active notes; "Unarchive {title}"(role=button) returns the chosen note to Notes. Every transition addresses that note's business identity and remains observable after reload.

Note actions revealed on hover remain keyboard-accessible. Actions are buttons except menu choices, which are menuitems; fields have associated accessible names. Note actions are scoped to the note region identified by its visible title.

**IMG-ARCHIVE-BUTTON · notes**

![IMG-ARCHIVE-BUTTON · notes](reference/archive_button.png)

**IMG-ARCHIVED-NOTES-PAGE · archived_notes**

![IMG-ARCHIVED-NOTES-PAGE · archived_notes](reference/archived_notes_page.png)

**IMG-UNARCHIVE-BUTTON · archived_notes**

![IMG-UNARCHIVE-BUTTON · archived_notes](reference/unarchive_button.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.2

**Scenarios:**

- SCN-REQ-2.4-01 — Archive a note into its separate list
  - **Step:** STEP-REQ-2.4-01-01
    - **Given:** Notes contains UI-created isolated Travel plans 2.5.1 with Trip itinerary and Active archive control with Stay active.
    - **When:** Hover Travel plans, click Archive {title}, open Archived in Sidebar, then return to Notes and reload.
    - **Then:** Note archived status exposes Undo; Archived notes contains exactly one Travel plans note with Trip itinerary and excludes the active control. After reload Notes excludes Travel plans and retains the active control with Stay active.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-ARCHIVE-BUTTON)`, `\ref[image](IMG-ARCHIVED-NOTES-PAGE)`, `\ref[image](IMG-UNARCHIVE-BUTTON)`
- SCN-REQ-2.4-02 — Undo archiving
  - **Step:** STEP-REQ-2.4-02-01
    - **Given:** Notes contains isolated Travel plans 2.5.2 with Return this itinerary.
    - **When:** Click Archive {title}, then Undo in Note archived status, and inspect Archived.
    - **Then:** Action undone appears, Notes restores the same title and content exactly once, and Archived excludes the restored note.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-ARCHIVE-BUTTON)`, `\ref[image](IMG-ARCHIVED-NOTES-PAGE)`, `\ref[image](IMG-UNARCHIVE-BUTTON)`
- SCN-REQ-2.4-03 — Unarchive the selected note
  - **Step:** STEP-REQ-2.4-03-01
    - **Given:** Create isolated Travel plans 2.5.4 with Selected itinerary and Other archived note with Other itinerary, archive both through UI, and open Archived where both are visible.
    - **When:** Hover only Travel plans, click its Unarchive {title}, then open Notes and reload.
    - **Then:** Archived removes only Travel plans and retains Other archived note with its content. Notes displays Travel plans exactly once with Selected itinerary after reload and excludes the other archived note.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-ARCHIVE-BUTTON)`, `\ref[image](IMG-ARCHIVED-NOTES-PAGE)`, `\ref[image](IMG-UNARCHIVE-BUTTON)`

### REQ-2.5 Pin and unpin notes

Clicking "Pin {title}"(role=button) moves that regular active note into Pinned notes exactly once and changes its pin action to "Unpin {title}"(role=button) with pressed=true. Unpin moves it back to Other notes and restores Pin with pressed=false. In Note editor, "Pin note"(role=button) toggles pressed state so closing the editor creates the note with the chosen pin state. These transitions preserve content, never duplicate the note, and survive reload.

Note actions revealed on hover remain keyboard-accessible. Actions are buttons except menu choices, which are menuitems; fields have associated accessible names. Note actions are scoped to the note region identified by its visible title.

**IMG-PIN-BUTTON · notes**

![IMG-PIN-BUTTON · notes](reference/pin_button.png)

**Type:** ATOMIC
**Dependencies:** REQ-2.2

**Scenarios:**

- SCN-REQ-2.5-01 — Pin an existing note
  - **Step:** STEP-REQ-2.5-01-01
    - **Given:** Notes contains isolated Meeting agenda 2.8.1 with Discuss the launch as a regular unpinned note.
    - **When:** Hover it, click Pin {title}, reload, and inspect its section and pin action.
    - **Then:** The same note and content appear exactly once in Pinned notes and not Other notes. Unpin {title} exposes pressed=true.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-PIN-BUTTON)`
- SCN-REQ-2.5-02 — Unpin an existing note
  - **Step:** STEP-REQ-2.5-02-01
    - **Given:** Create isolated Meeting agenda 2.8.2 with Keep meeting content through Note editor with Pin note selected.
    - **When:** Hover the saved pinned note, click Unpin {title}, reload, and inspect its section and action.
    - **Then:** The note appears exactly once only in Other notes with unchanged content; Pin {title} exposes pressed=false.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-PIN-BUTTON)`
- SCN-REQ-2.5-03 — Create a pinned note
  - **Step:** STEP-REQ-2.5-03-01
    - **Given:** Notes is open and the isolated Pinned at creation title is unused.
    - **When:** Open Note editor, enter that title and Pinned creation content, click Pin note, click Close, and reload.
    - **Then:** The note and content persist exactly once only in Pinned notes, and its Unpin {title} action exposes pressed=true.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-PIN-BUTTON)`
