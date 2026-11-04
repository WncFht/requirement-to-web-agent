# Keep personal note management

A personal note management application for creating, editing, organizing, searching, archiving, and deleting notes.

The interface uses en-US. Tested note states are established through normal user actions in a single application instance. No fixed benchmark clock or historical deleted-note seed data is required.

## REQ-1 Workspace navigation

Entry workspace and sidebar navigation.

The personal workspace requires no authentication or reminder scheduler. Sidebar navigation actions expose current state when selected.

**Type:** FOLDER
**Dependencies:** None

### REQ-1.1 Open and navigate the personal workspace

Opening the application displays a personal notes workspace with the "Sidebar"(role=navigation) expanded and "Notes"(role=button) selected. The sidebar provides "Reminders"(role=button), user-label actions, "Edit Labels"(role=button), "Archived"(role=button), and "Trash"(role=button), each with an identifiable icon; Reminders is a default label with its own icon. Users can find notes through "Search"(role=searchbox), begin creation with "Take a note"(role=button), open settings through "Settings menu"(role=button), and switch the initial layout through "List view"(role=button). "Toggle sidebar"(role=button) collapses the sidebar to icons and expands it again, exposing its expanded state while preserving accessible navigation names. Text labels disappear when collapsed and return when expanded. Alignment, hover feedback, selected-item highlighting, and appearance follow the visual references; screenshot similarity is not a functional oracle.

The personal workspace requires no authentication or reminder scheduler. Sidebar navigation actions expose current state when selected.

This is a personal workspace without authentication or a reminder scheduler; Reminders is a label, not a scheduled notification feature. The interface uses en-US.

**IMG-HOME-PAGE · notes**

![IMG-HOME-PAGE · notes](reference/home_page.png)

**IMG-SIDEBAR · notes**

![IMG-SIDEBAR · notes](reference/sidebar.png)

**IMG-SIDEBAR-COLLAPSED · notes**

![IMG-SIDEBAR-COLLAPSED · notes](reference/sidebar_collapsed.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-1.1-01 — Open the workspace
  - **Step:** STEP-REQ-1.1-01-01
    - **Given:** A fresh browser opens the personal workspace without authentication; default label exists, the default layout is grid, and the sidebar starts expanded with Notes selected.
      Seed prerequisites (prepared before this scenario):
      - default label: {"name": "Reminders", "icon": "distinct reminder icon"}
    - **When:** Open the application entry and inspect "Sidebar"(role=navigation), its Notes, Reminders, Archived, Trash and Edit Labels buttons, and the Search searchbox, Settings menu, List view and Take a note buttons.
    - **Then:** Sidebar is visible; Toggle sidebar reports expanded=true and Notes reports current=true. Each named sidebar action and each workspace control is visible, including the default Reminders action.
    - **References:** `\ref[image](IMG-HOME-PAGE)`, `\ref[image](IMG-SIDEBAR)`, `\ref[image](IMG-SIDEBAR-COLLAPSED)`
- SCN-REQ-1.1-02 — Collapse and expand the sidebar
  - **Step:** STEP-REQ-1.1-02-01
    - **Given:** The entry workspace is open with Sidebar expanded, Notes selected, and Toggle sidebar reporting expanded=true.
      Seed prerequisites (prepared before this scenario):
      - default label: {"name": "Reminders", "icon": "distinct reminder icon"}
    - **When:** Click "Toggle sidebar"(role=button), inspect sidebar text and accessible actions, then click the same button again.
    - **Then:** After collapse, expanded=false and the visible Notes text is hidden while Notes, Reminders, Archived and Trash remain accessible and visible as actions. After expansion, expanded=true and the Notes text is visible again.
    - **References:** `\ref[image](IMG-HOME-PAGE)`, `\ref[image](IMG-SIDEBAR)`, `\ref[image](IMG-SIDEBAR-COLLAPSED)`

## REQ-2 Manage the note lifecycle

All note states are created and changed through the personal workspace UI.

Note actions revealed on hover remain keyboard-accessible. Actions are buttons except menu choices, which are menuitems; fields have associated accessible names. Note actions are scoped to the note region identified by its visible title.

Personal notes are created through Take a note, using the scenario-supplied content. Note titles retain the source example title plus a deterministic run/worker/case suffix. Mutable note states and action notifications are produced by note actions, including delete, archive and Undo; they are not preloaded.

**Type:** FOLDER
**Dependencies:** None

### REQ-2.1 List pinned and regular notes separately

The active Notes view separates pinned notes into exactly one "Pinned notes"(role=region) and regular notes into exactly one "Other notes"(role=region). Every active note appears once in the appropriate section as "{title}"(role=region), whose accessible name equals that note's visible title. Archived and trashed notes do not appear in either section. Business identity identifies each note regardless of whether the presentation uses cards, a table, or another layout.

Note actions revealed on hover remain keyboard-accessible. Actions are buttons except menu choices, which are menuitems; fields have associated accessible names. Note actions are scoped to the note region identified by its visible title.

This is a personal workspace without authentication or a reminder scheduler; Reminders is a label, not a scheduled notification feature. The interface uses en-US.

Note titles accept the source example name plus a deterministic run/worker/case suffix. Notes and their mutable action states are produced by the described note interactions.

**IMG-HOME-PAGE · notes**

![IMG-HOME-PAGE · notes](reference/home_page.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-2.1-01 — Separate pinned and regular notes
  - **Step:** STEP-REQ-2.1-01-01
    - **Given:** Notes is open. Through Take a note, Title, Content and Close, create a case-isolated Sprint goals note with Finish the sprint and Pin note selected, and a regular Groceries note with Milk and bread.
    - **When:** Inspect the "Pinned notes"(role=region) and "Other notes"(role=region) collections using each note's full isolated title.
    - **Then:** Each collection exists once. Sprint goals appears exactly once only in Pinned notes and Groceries exactly once only in Other notes; neither note is duplicated across sections and each remains visible with its saved content.
    - **References:** `\ref[requirement](REQ-2.9)`, `\ref[image](IMG-HOME-PAGE)`

### REQ-2.2 Create and autosave a personal note

Clicking "Take a note"(role=button) opens "Note editor"(role=dialog), where users enter "Title"(role=textbox) and "Content"(role=textbox). Clicking "Close"(role=button) closes the editor and automatically saves one active note with the entered title and content; the note survives reload without an explicit save action. Creation accepts the nonempty titles and multiline content used in the scenarios; empty-input rules are unspecified. The editor also provides Pin note, Background color, and Change labels for their corresponding behaviors.

Note actions revealed on hover remain keyboard-accessible. Actions are buttons except menu choices, which are menuitems; fields have associated accessible names. Note actions are scoped to the note region identified by its visible title.

This is a personal workspace without authentication or a reminder scheduler; Reminders is a label, not a scheduled notification feature. The interface uses en-US.

Note titles accept the source example name plus a deterministic run/worker/case suffix. Notes and their mutable action states are produced by the described note interactions.

**IMG-CREATE-NOTE-HOME-PAGE · notes**

![IMG-CREATE-NOTE-HOME-PAGE · notes](reference/create_note_home_page.png)

**IMG-CREATE-NOTE-FORM · notes**

![IMG-CREATE-NOTE-FORM · notes](reference/create_note_form.png)

**Type:** ATOMIC
**Dependencies:** None

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

This is a personal workspace without authentication or a reminder scheduler; Reminders is a label, not a scheduled notification feature. The interface uses en-US.

Note titles accept the source example name plus a deterministic run/worker/case suffix. Notes and their mutable action states are produced by the described note interactions.

**IMG-NOTE-EDITING · notes**

![IMG-NOTE-EDITING · notes](reference/note_editing.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-2.3-01 — Save an edited note
  - **Step:** STEP-REQ-2.3-01-01
    - **Given:** Notes contains a UI-created case-isolated Project ideas note with Initial editable content, created through Take a note, Title, Content and Close.
    - **When:** Click "Open {title}"(role=button) within that note; verify Title and Content are prefilled, replace Content with Updated editable content, click Close, and reload.
    - **Then:** The editor initially contains the saved title and content, then closes. After reload exactly one note retains the original title and replacement content, with no Initial editable content in that note.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-NOTE-EDITING)`

### REQ-2.4 Delete notes and recover through notification Undo

Users reveal a note's actions by hovering if necessary, then click "More options {title}"(role=button) and choose "Delete Note"(role=menuitem). Deletion immediately removes that note from active Notes, moves it to Trash without an additional confirmation, and displays "Note deleted"(role=status) with "Undo"(role=button) and "Dismiss notification"(role=button). Undo restores the same title and content to active Notes, removes the note from Trash, and displays "Action undone"(role=status). Dismiss notification closes the notification without reversing deletion; the same deleted note and its content remain in Trash after reload. Automatic notification dismissal and its timing are outside the acceptance scope; no elapsed-time wait is required.

Note actions revealed on hover remain keyboard-accessible. Actions are buttons except menu choices, which are menuitems; fields have associated accessible names. Note actions are scoped to the note region identified by its visible title.

This is a personal workspace without authentication or a reminder scheduler; Reminders is a label, not a scheduled notification feature. The interface uses en-US.

Note titles accept the source example name plus a deterministic run/worker/case suffix. Notes and their mutable action states are produced by the described note interactions.

**IMG-NOTE-MORE-OPTIONS-DROPDOWN · notes**

![IMG-NOTE-MORE-OPTIONS-DROPDOWN · notes](reference/note_more_options_dropdown.png)

**IMG-NOTE-DELETE-NOTIFICATION · notes**

![IMG-NOTE-DELETE-NOTIFICATION · notes](reference/note_delete_notification.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-2.4-01 — Move a deleted note to Trash
  - **Step:** STEP-REQ-2.4-01-01
    - **Given:** Notes contains the UI-created isolated Delete me 2.3.1 note with Deletion preserves this content.
    - **When:** Hover that note if necessary, click More options {title}, choose Delete Note from the menu, then click Trash in Sidebar.
    - **Then:** Deletion opens no confirmation dialog and removes the note from Notes immediately. Note deleted status exposes Undo, and Trash contains exactly one note with the same title and content.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-NOTE-MORE-OPTIONS-DROPDOWN)`, `\ref[image](IMG-NOTE-DELETE-NOTIFICATION)`
- SCN-REQ-2.4-02 — Undo deletion
  - **Step:** STEP-REQ-2.4-02-01
    - **Given:** Notes contains the UI-created isolated Delete me 2.3.2 note with Undo restores this content.
    - **When:** Use More options {title} and Delete Note, click Undo within Note deleted status, then open Trash.
    - **Then:** Action undone status appears and Notes again contains exactly one note with the same title and content. The restored note is absent from Trash.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-NOTE-MORE-OPTIONS-DROPDOWN)`, `\ref[image](IMG-NOTE-DELETE-NOTIFICATION)`
- SCN-REQ-2.4-03 — Dismiss deletion notifications
  - **Step:** STEP-REQ-2.4-03-01
    - **Given:** Notes contains the UI-created isolated Manual dismissal note with Dismissal preserves deleted content.
    - **When:** Delete the note through its menu, click Dismiss notification in Note deleted status, then open Trash and reload.
    - **Then:** The notification closes without Undo. The note stays absent from active Notes, while Trash retains exactly one note with the same title and content before and after reload.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-NOTE-MORE-OPTIONS-DROPDOWN)`, `\ref[image](IMG-NOTE-DELETE-NOTIFICATION)`

### REQ-2.5 Inspect and empty Trash with persistent deleted notes

Clicking "Trash"(role=button) displays deleted notes in "Deleted notes"(role=region), excluding active and archived notes. Deleted notes retain their titles and contents across navigation and reload until a user action restores or permanently removes them. "Empty Trash"(role=button) permanently removes all currently deleted notes while preserving active notes. If confirmation is offered, it appears as "Empty Trash"(role=dialog) with an "Empty Trash"(role=button) confirmation action. All scenarios use the same application instance and entry URL. Automatic age-based deletion is outside the acceptance scope.

Note actions revealed on hover remain keyboard-accessible. Actions are buttons except menu choices, which are menuitems; fields have associated accessible names. Note actions are scoped to the note region identified by its visible title.

Each scenario creates and deletes its own isolated notes through the UI. No historical notes, backdated deletion timestamps or special startup data are required.

This is a personal workspace without authentication or a reminder scheduler; Reminders is a label, not a scheduled notification feature. The interface uses en-US.

Note titles accept the source example name plus a deterministic run/worker/case suffix. Notes and their mutable action states are produced by the described note interactions.

**IMG-HOME-PAGE · notes**

![IMG-HOME-PAGE · notes](reference/home_page.png)

**IMG-TRASH-LIST · trash**

![IMG-TRASH-LIST · trash](reference/trash_list.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-2.5-01 — Keep a deleted note in Trash after reload
  - **Step:** STEP-REQ-2.5-01-01
    - **Given:** Through Take a note, Title, Content and Close, create the isolated Trash persistence note with Deleted content survives reload, then delete it through its More options menu.
    - **When:** Open Trash in Sidebar, reload the page, then select Notes.
    - **Then:** Deleted notes contains exactly one note with the saved title and content after reload. The same deleted note remains absent from active Notes.
    - **References:** `\ref[requirement](REQ-2.4)`, `\ref[image](IMG-HOME-PAGE)`, `\ref[image](IMG-TRASH-LIST)`
- SCN-REQ-2.5-02 — Show deleted notes separately
  - **Step:** STEP-REQ-2.5-02-01
    - **Given:** Through normal note creation, create isolated Delete me 2.3.3 with Recently deleted content and Movie list with Active control content; delete only Delete me 2.3.3 through its menu.
    - **When:** Click Trash in Sidebar and inspect Deleted notes.
    - **Then:** The deleted note appears exactly once with its saved content; the active Movie list note is absent from Trash.
    - **References:** `\ref[requirement](REQ-2.4)`, `\ref[image](IMG-HOME-PAGE)`, `\ref[image](IMG-TRASH-LIST)`
- SCN-REQ-2.5-03 — Empty Trash without deleting active notes
  - **Step:** STEP-REQ-2.5-03-01
    - **Given:** Create isolated Empty trash A with Discard A, Empty trash B with Discard B and Active control with Keep active content. Delete A and B through UI and open Trash, confirming both deleted notes are present.
    - **When:** Click Empty Trash. If an Empty Trash dialog is offered, click its Empty Trash confirmation button. Reload Trash, then click Notes.
    - **Then:** Deleted notes contains no note regions before and after reload. Active control remains exactly once with its content, while deleted A and B remain absent from Notes.
    - **References:** `\ref[requirement](REQ-2.4)`, `\ref[image](IMG-HOME-PAGE)`, `\ref[image](IMG-TRASH-LIST)`

### REQ-2.6 Archive notes and restore them to active Notes

Clicking "Archive {title}"(role=button) moves the selected active note out of Notes into "Archived notes"(role=region) and displays "Note archived"(role=status) with "Undo"(role=button). Undo restores the same note and content to Notes, removes it from the archive, and shows Action undone. Clicking "Archived"(role=button) displays archived notes separately from active notes; "Unarchive {title}"(role=button) returns the chosen note to Notes. Every transition addresses that note's business identity and remains observable after reload.

Note actions revealed on hover remain keyboard-accessible. Actions are buttons except menu choices, which are menuitems; fields have associated accessible names. Note actions are scoped to the note region identified by its visible title.

This is a personal workspace without authentication or a reminder scheduler; Reminders is a label, not a scheduled notification feature. The interface uses en-US.

Note titles accept the source example name plus a deterministic run/worker/case suffix. Notes and their mutable action states are produced by the described note interactions.

**IMG-ARCHIVE-BUTTON · notes**

![IMG-ARCHIVE-BUTTON · notes](reference/archive_button.png)

**IMG-ARCHIVED-NOTES-PAGE · archived_notes**

![IMG-ARCHIVED-NOTES-PAGE · archived_notes](reference/archived_notes_page.png)

**IMG-UNARCHIVE-BUTTON · archived_notes**

![IMG-UNARCHIVE-BUTTON · archived_notes](reference/unarchive_button.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-2.6-01 — Archive a note into its separate list
  - **Step:** STEP-REQ-2.6-01-01
    - **Given:** Notes contains UI-created isolated Travel plans 2.5.1 with Trip itinerary and Active archive control with Stay active.
    - **When:** Hover Travel plans, click Archive {title}, open Archived in Sidebar, then return to Notes and reload.
    - **Then:** Note archived status exposes Undo; Archived notes contains exactly one Travel plans note with Trip itinerary and excludes the active control. After reload Notes excludes Travel plans and retains the active control with Stay active.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-ARCHIVE-BUTTON)`, `\ref[image](IMG-ARCHIVED-NOTES-PAGE)`, `\ref[image](IMG-UNARCHIVE-BUTTON)`
- SCN-REQ-2.6-02 — Undo archiving
  - **Step:** STEP-REQ-2.6-02-01
    - **Given:** Notes contains isolated Travel plans 2.5.2 with Return this itinerary.
    - **When:** Click Archive {title}, then Undo in Note archived status, and inspect Archived.
    - **Then:** Action undone appears, Notes restores the same title and content exactly once, and Archived excludes the restored note.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-ARCHIVE-BUTTON)`, `\ref[image](IMG-ARCHIVED-NOTES-PAGE)`, `\ref[image](IMG-UNARCHIVE-BUTTON)`
- SCN-REQ-2.6-03 — Unarchive the selected note
  - **Step:** STEP-REQ-2.6-03-01
    - **Given:** Create isolated Travel plans 2.5.4 with Selected itinerary and Other archived note with Other itinerary, archive both through UI, and open Archived where both are visible.
    - **When:** Hover only Travel plans, click its Unarchive {title}, then open Notes and reload.
    - **Then:** Archived removes only Travel plans and retains Other archived note with its content. Notes displays Travel plans exactly once with Selected itinerary after reload and excludes the other archived note.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-ARCHIVE-BUTTON)`, `\ref[image](IMG-ARCHIVED-NOTES-PAGE)`, `\ref[image](IMG-UNARCHIVE-BUTTON)`

### REQ-2.7 Apply note background colors

Clicking "Background color {title}"(role=button) on an existing note, or "Background color"(role=button) in Note editor, opens a palette where "Light green"(role=button) applies a visibly light-green background to the note itself. The existing-note control then identifies the selection as "Background color {title}: Light green"(role=button). Notes created with this selection autosave with the same background, and selected colors persist after reload. Changing only a palette or badge is insufficient; the reference guides the appearance without prescribing a CSS token or exact RGB value.

Note actions revealed on hover remain keyboard-accessible. Actions are buttons except menu choices, which are menuitems; fields have associated accessible names. Note actions are scoped to the note region identified by its visible title.

This is a personal workspace without authentication or a reminder scheduler; Reminders is a label, not a scheduled notification feature. The interface uses en-US.

Note titles accept the source example name plus a deterministic run/worker/case suffix. Notes and their mutable action states are produced by the described note interactions.

**IMG-NOTE-COLORING · notes**

![IMG-NOTE-COLORING · notes](reference/note_coloring.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-2.7-01 — Color an existing note
  - **Step:** STEP-REQ-2.7-01-01
    - **Given:** Notes contains isolated Garden tasks existing with Water the herbs, created through the normal editor.
    - **When:** Hover that note, click Background color {title}, choose Light green, then reload and inspect the note and its color action.
    - **Then:** The same note and content persist. Its surface has a light-green background and its action reads Background color {title}: Light green; a changed action name alone is insufficient.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-NOTE-COLORING)`
- SCN-REQ-2.7-02 — Create a colored note
  - **Step:** STEP-REQ-2.7-02-01
    - **Given:** Notes is open and no note uses the isolated Garden tasks created title.
    - **When:** Click Take a note, enter that title and Plant spring herbs, click Background color in Note editor and choose Light green, then Close and reload.
    - **Then:** Exactly one note retains the entered content with a light-green surface and Background color {title}: Light green action after reload.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-NOTE-COLORING)`

### REQ-2.8 Assign and remove note labels

Users open a note's More options menu and choose "Change labels"(role=menuitem), or click "Change labels"(role=button) in Note editor, to open "Note labels"(role=dialog). Each available label is selectable through "{label}"(role=checkbox). Users may assign one or more labels, or clear a checked label to remove its assignment; "Done"(role=button) closes the chooser and retains the selections. Assigned labels appear visibly on the note, drive sidebar filtering consistently, and persist after closing and reload. The default Reminders label is available when creating a note.

Note actions revealed on hover remain keyboard-accessible. Actions are buttons except menu choices, which are menuitems; fields have associated accessible names. Note actions are scoped to the note region identified by its visible title.

This is a personal workspace without authentication or a reminder scheduler; Reminders is a label, not a scheduled notification feature. The interface uses en-US.

Note titles accept the source example name plus a deterministic run/worker/case suffix. Notes and their mutable action states are produced by the described note interactions.

**IMG-ASSIGN-LABEL-TO-NOTE · notes**

![IMG-ASSIGN-LABEL-TO-NOTE · notes](reference/assign_label_to_note.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-2.8-01 — Assign multiple labels and filter by either
  - **Step:** STEP-REQ-2.8-01-01
    - **Given:** Through Edit Labels, New label and Create label, create isolated Work and Personal labels. Create isolated Team retro add label with Retro decisions and no assigned labels.
    - **When:** On that note choose More options {title} then Change labels; check Work and Personal in Note labels, click Done, reload, and select each label in Sidebar in turn.
    - **Then:** Both labels are visible on the note after reload. Either sidebar selection displays exactly one matching note with the same title and Retro decisions.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[requirement](REQ-3.1)`, `\ref[image](IMG-ASSIGN-LABEL-TO-NOTE)`
- SCN-REQ-2.8-02 — Remove an assigned label
  - **Step:** STEP-REQ-2.8-02-01
    - **Given:** Create isolated Work and two notes through UI, Team retro remove label with Remove membership and Other Work note with Keep membership; assign Work to both through the editor's Change labels chooser.
    - **When:** Open Change labels for Team retro, clear its Work checkbox and click Done; reload, then select Work in Sidebar.
    - **Then:** Work no longer appears on Team retro. The Work-filtered list excludes that note and retains Other Work note exactly once with Keep membership.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[requirement](REQ-3.1)`, `\ref[image](IMG-ASSIGN-LABEL-TO-NOTE)`
- SCN-REQ-2.8-03 — Create a note with Reminders
  - **Step:** STEP-REQ-2.8-03-01
    - **Given:** The default Reminders label exists and Notes is open; the isolated Call dentist created title is unused.
      Seed prerequisites (prepared before this scenario):
      - default label: {"name": "Reminders", "icon": "distinct reminder icon"}
    - **When:** Open Note editor, enter that title and Arrange the appointment, choose Change labels, check Reminders, click Done and Close, then select Reminders in Sidebar.
    - **Then:** The saved note visibly carries Reminders and appears exactly once with Arrange the appointment in the Reminders-filtered list.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-ASSIGN-LABEL-TO-NOTE)`

### REQ-2.9 Pin and unpin notes

Clicking "Pin {title}"(role=button) moves that regular active note into Pinned notes exactly once and changes its pin action to "Unpin {title}"(role=button) with pressed=true. Unpin moves it back to Other notes and restores Pin with pressed=false. In Note editor, "Pin note"(role=button) toggles pressed state so closing the editor creates the note with the chosen pin state. These transitions preserve content, never duplicate the note, and survive reload.

Note actions revealed on hover remain keyboard-accessible. Actions are buttons except menu choices, which are menuitems; fields have associated accessible names. Note actions are scoped to the note region identified by its visible title.

This is a personal workspace without authentication or a reminder scheduler; Reminders is a label, not a scheduled notification feature. The interface uses en-US.

Note titles accept the source example name plus a deterministic run/worker/case suffix. Notes and their mutable action states are produced by the described note interactions.

**IMG-PIN-BUTTON · notes**

![IMG-PIN-BUTTON · notes](reference/pin_button.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-2.9-01 — Pin an existing note
  - **Step:** STEP-REQ-2.9-01-01
    - **Given:** Notes contains isolated Meeting agenda 2.8.1 with Discuss the launch as a regular unpinned note.
    - **When:** Hover it, click Pin {title}, reload, and inspect its section and pin action.
    - **Then:** The same note and content appear exactly once in Pinned notes and not Other notes. Unpin {title} exposes pressed=true.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-PIN-BUTTON)`
- SCN-REQ-2.9-02 — Unpin an existing note
  - **Step:** STEP-REQ-2.9-02-01
    - **Given:** Create isolated Meeting agenda 2.8.2 with Keep meeting content through Note editor with Pin note selected.
    - **When:** Hover the saved pinned note, click Unpin {title}, reload, and inspect its section and action.
    - **Then:** The note appears exactly once only in Other notes with unchanged content; Pin {title} exposes pressed=false.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-PIN-BUTTON)`
- SCN-REQ-2.9-03 — Create a pinned note
  - **Step:** STEP-REQ-2.9-03-01
    - **Given:** Notes is open and the isolated Pinned at creation title is unused.
    - **When:** Open Note editor, enter that title and Pinned creation content, click Pin note, click Close, and reload.
    - **Then:** The note and content persist exactly once only in Pinned notes, and its Unpin {title} action exposes pressed=true.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-PIN-BUTTON)`

## REQ-3 Organize with labels

User-created labels and the default Reminders label organize active notes.

User labels are created through Edit Labels. Each label retains its source example name plus a deterministic run/worker/case suffix.

**Type:** FOLDER
**Dependencies:** None

### REQ-3.1 Create user labels

Clicking "Edit Labels"(role=button) opens "Edit Labels"(role=dialog). Users enter a nonempty name in "New label"(role=textbox) and click "Create label"(role=button), adding that label exactly once to management and the sidebar. Its editable name appears in "Label name {label}"(role=textbox), and the sidebar exposes "{label}"(role=button) for filtering. "Done"(role=button) closes management, and the created label persists after reload. Each scenario creates its own business identity; empty-name and duplicate-name validation are unspecified.

This is a personal workspace without authentication or a reminder scheduler; Reminders is a label, not a scheduled notification feature. The interface uses en-US.

User-label names accept the source example name plus a deterministic run/worker/case suffix. User labels are created through Edit Labels, while the default Reminders label already exists.

**IMG-MANAGE-LABELS · notes**

![IMG-MANAGE-LABELS · notes](reference/manage_labels.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-3.1-01 — Create a user label
  - **Step:** STEP-REQ-3.1-01-01
    - **Given:** Notes is open with the default Reminders label; the isolated New user label name does not exist.
      Seed prerequisites (prepared before this scenario):
      - default label: {"name": "Reminders", "icon": "distinct reminder icon"}
    - **When:** Click Edit Labels, enter the isolated name in New label, click Create label and Done; reload, reopen Edit Labels and inspect Label name {label}.
    - **Then:** Sidebar exposes exactly one visible action with the new label name, and management exposes exactly one Label name {label} field containing that name. Done closes management.
    - **References:** `\ref[requirement](REQ-1.1)`, `\ref[image](IMG-MANAGE-LABELS)`

### REQ-3.2 Filter Notes through sidebar labels

Clicking "{label}"(role=button) within "Sidebar"(role=navigation) displays only active notes assigned that label, each exactly once, and exposes current=true on the selected navigation action. "Notes"(role=button) clears the label filter and restores the complete active list. The always-present "Reminders"(role=button), with its own icon, filters by the default label in the same way. Both sidebar actions and labels on notes are identified by business identity rather than position.

This is a personal workspace without authentication or a reminder scheduler; Reminders is a label, not a scheduled notification feature. The interface uses en-US.

User-label names accept the source example name plus a deterministic run/worker/case suffix. User labels are created through Edit Labels, while the default Reminders label already exists.

**IMG-SIDEBAR · notes**

![IMG-SIDEBAR · notes](reference/sidebar.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-3.2-01 — Filter by a user label
  - **Step:** STEP-REQ-3.2-01-01
    - **Given:** Create isolated Work and two notes through UI, Design review with Work design decisions assigned Work and unlabeled Movie list with An unlabeled movie note.
    - **When:** Select the Work button in Sidebar.
    - **Then:** Exactly one Design review note displays its saved content; Movie list is hidden and the selected Work action exposes current=true.
    - **References:** `\ref[requirement](REQ-2.8)`, `\ref[requirement](REQ-3.1)`, `\ref[image](IMG-SIDEBAR)`
- SCN-REQ-3.2-02 — Return to the complete notes list
  - **Step:** STEP-REQ-3.2-02-01
    - **Given:** Create isolated Work, Design review with Design details assigned Work, and Movie list with Movie details. Select Work and verify Movie list is hidden.
    - **When:** Click Notes in Sidebar.
    - **Then:** Both notes reappear exactly once with their saved contents, and Notes exposes current=true.
    - **References:** `\ref[requirement](REQ-2.8)`, `\ref[requirement](REQ-3.1)`, `\ref[image](IMG-SIDEBAR)`
- SCN-REQ-3.2-03 — Filter by the default Reminders label
  - **Step:** STEP-REQ-3.2-03-01
    - **Given:** Create isolated Call dentist existing with Dentist details assigned Reminders and unlabeled Movie list with Movie details through the editor.
      Seed prerequisites (prepared before this scenario):
      - default label: {"name": "Reminders", "icon": "distinct reminder icon"}
    - **When:** Click Reminders in Sidebar.
    - **Then:** The reminder note appears exactly once with Dentist details, Movie list is hidden, and Reminders exposes current=true.
    - **References:** `\ref[requirement](REQ-2.8)`, `\ref[image](IMG-SIDEBAR)`

### REQ-3.3 Rename and delete user labels

Clicking "Edit Labels"(role=button) opens "Edit Labels"(role=dialog), where each user label is identified by its business name. Users change "Label name {label}"(role=textbox) and click "Save label {label}"(role=button), whose original action identity remains available until saving. Rename updates the sidebar's "{label}"(role=button) and labels on notes without losing membership. Clicking "Delete label {label}"(role=button) removes the label from the sidebar and assigned notes while preserving their content. "Done"(role=button) closes management; renames and deletions persist after reload. Modifying Reminders is outside scope.

This is a personal workspace without authentication or a reminder scheduler; Reminders is a label, not a scheduled notification feature. The interface uses en-US.

User-label names accept the source example name plus a deterministic run/worker/case suffix. User labels are created through Edit Labels, while the default Reminders label already exists.

**IMG-MANAGE-LABELS · notes**

![IMG-MANAGE-LABELS · notes](reference/manage_labels.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-3.3-01 — Rename a label and retain membership
  - **Step:** STEP-REQ-3.3-01-01
    - **Given:** Create isolated Work editable and a Label rename control note with Retain label membership assigned to it through UI.
    - **When:** Open Edit Labels, replace Label name {original} with isolated Work renamed, click Save label {original} and Done; reload and select the renamed sidebar label.
    - **Then:** Sidebar contains the renamed label once and no original label. The note displays the new label without the old one, and filtering by the new name still finds the same note and content.
    - **References:** `\ref[requirement](REQ-2.8)`, `\ref[image](IMG-MANAGE-LABELS)`
- SCN-REQ-3.3-02 — Delete a label without deleting its note
  - **Step:** STEP-REQ-3.3-02-01
    - **Given:** Create isolated Disposable label and Label delete control with Keep this labeled note assigned to that label.
    - **When:** Open Edit Labels, click Delete label {label}, click Done, and reload.
    - **Then:** The deleted label is absent from Sidebar and the note, while the note remains exactly once with unchanged title and Keep this labeled note.
    - **References:** `\ref[requirement](REQ-2.8)`, `\ref[image](IMG-MANAGE-LABELS)`

## REQ-4 Find personal notes

Search results follow keyword and suggested-filter criteria.

**Type:** FOLDER
**Dependencies:** None

### REQ-4.1 Search keywords and suggested filters

Entering a keyword in "Search"(role=searchbox) filters active notes by case-insensitive title or content matches. Each matching fragment appears as "Highlight {keyword}"(role=region) within its note, displays only the matching text, and is visibly distinguished from surrounding text without requiring a particular element or CSS class. Searching st includes Study schedule by title and a separate note containing st only in its content, while excluding notes with neither match. Focusing Search displays "Suggested filters"(role=region); choosing "Reminders"(role=button) there filters active notes by the default label. Clearing Search and selecting Notes restores the full active list.

The current search is produced by Search input or Suggested filters selection; no search state is preloaded.

This is a personal workspace without authentication or a reminder scheduler; Reminders is a label, not a scheduled notification feature. The interface uses en-US.

**IMG-SEARCH-SUGGESTED-FILTERS · notes**

![IMG-SEARCH-SUGGESTED-FILTERS · notes](reference/search_suggested_filters.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-4.1-01 — Search title and content with highlights
  - **Step:** STEP-REQ-4.1-01-01
    - **Given:** Through UI create isolated Study schedule with Math on Monday, Reading plan with Read a story, and Ocean memo with Calm blue waves. Isolation suffixes cannot introduce the keyword st.
    - **When:** Enter st in Search; inspect each matching note's Highlight st region. Clear Search and click Notes.
    - **Then:** Study schedule and Reading plan appear once while Ocean memo is hidden; each match has a visible highlight region whose text is only st, case-insensitively. Clearing restores all three notes with their contents.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-SEARCH-SUGGESTED-FILTERS)`
- SCN-REQ-4.1-02 — Choose a suggested label filter
  - **Step:** STEP-REQ-4.1-02-01
    - **Given:** Create isolated Call dentist existing with Reminder content assigned Reminders and unlabeled Movie list with Unlabeled content.
      Seed prerequisites (prepared before this scenario):
      - default label: {"name": "Reminders", "icon": "distinct reminder icon"}
    - **When:** Focus Search, click Reminders within Suggested filters, then clear Search and select Notes.
    - **Then:** Suggested filters is visible on focus; its Reminders choice includes only the reminder note. Clearing restores both notes exactly once with their saved contents.
    - **References:** `\ref[requirement](REQ-2.8)`, `\ref[image](IMG-SEARCH-SUGGESTED-FILTERS)`

## REQ-5 Configure the workspace

Settings and note layouts are user observable configuration behaviors.

**Type:** FOLDER
**Dependencies:** None

### REQ-5.1 Open and save or cancel application settings

Clicking "Settings menu"(role=button) opens a menu; choosing "Settings"(role=menuitem) opens "Settings"(role=dialog). Users configure "Add new items to the bottom"(role=checkbox) and "Move checked items to bottom"(role=checkbox), then click "Save"(role=button) to commit the options and close, or "Cancel"(role=button) to close without applying pending changes. Reopening reflects saved selections and discards canceled edits, and saved selections survive reload. These options do not introduce additional checklist or list-item behavior beyond the source.

Saved setting selections are produced through Settings and Save. Initial setting values are not fixed by the requirements.

This is a personal workspace without authentication or a reminder scheduler; Reminders is a label, not a scheduled notification feature. The interface uses en-US.

**IMG-SETTINGS-DROPDOWN · notes**

![IMG-SETTINGS-DROPDOWN · notes](reference/settings_dropdown.png)

**IMG-SETTINGS-SETTINGS · notes**

![IMG-SETTINGS-SETTINGS · notes](reference/settings_settings.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-5.1-01 — Save settings and discard canceled changes
  - **Step:** STEP-REQ-5.1-01-01
    - **Given:** Notes is open. Open Settings menu, choose Settings and record the current Add new items to the bottom checkbox value; Move checked items to bottom, Save and Cancel are available.
    - **When:** Toggle Add new items to the bottom to the opposite value and click Save. Reload and reopen Settings, toggle it back but click Cancel, then reopen once more.
    - **Then:** Save closes the dialog and the saved value survives reload. Cancel closes the dialog without committing its pending toggle; reopening still shows the previously saved value.
    - **References:** `\ref[requirement](REQ-1.1)`, `\ref[image](IMG-SETTINGS-DROPDOWN)`, `\ref[image](IMG-SETTINGS-SETTINGS)`

### REQ-5.2 Switch between default grid and list layouts

A fresh workspace displays a grid in "Notes"(role=region) with an accessible description identifying Grid view. Clicking "List view"(role=button) changes the same notes to a single-column list, updates that description to List view, and offers "Grid view"(role=button). Grid view restores the grid and List view action. At the evaluator desktop viewport, populated grid cards occupy multiple columns while list surfaces align in one column; switching preserves titles, content, and note count. Appearance follows the visual references.

This is a personal workspace without authentication or a reminder scheduler; Reminders is a label, not a scheduled notification feature. The interface uses en-US.

**IMG-HOME-PAGE · notes**

![IMG-HOME-PAGE · notes](reference/home_page.png)

**IMG-LIST-VIEW · notes**

![IMG-LIST-VIEW · notes](reference/list_view.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-5.2-01 — Switch grid to list and back
  - **Step:** STEP-REQ-5.2-01-01
    - **Given:** At the evaluator desktop viewport, Notes starts with Grid view accessible description and List view action. Create isolated View alpha, View beta and View gamma notes, each with Layout content.
    - **When:** Click List view and inspect the three note surfaces, then click Grid view and inspect them again.
    - **Then:** List mode reports List view, offers Grid view, and aligns nonoverlapping notes in one column; grid mode reports Grid view, offers List view and arranges populated cards across multiple columns. Both modes retain exactly one of each note and its content without prescribing exact pixel widths.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-HOME-PAGE)`, `\ref[image](IMG-LIST-VIEW)`
