# UI Guidelines

This document describes the design and function of the Bundle Maker's ncurses
user interface elements.

## General Notes

- Dimensions are given in character grid sizes (1 unit = 1 character).
- Dimensions are assumed full width unless specified otherwise.
- Colors are referred to by name; a separate table translates these names to 256
  ANSI color codes.
- Key bindings are case-insensitive and generally single key presses, except for
  standard terminal combinations like Ctrl+D and Ctrl+C.
- The application assumes a minimal 80x24 terminal size. If the terminal is
  smaller, the design gets clipped.
- Element sizing and positioning are anchored to the screen's top or bottom
  rows. Elements stretch from the top down when the terminal is larger than the
  minimum size.
- For example, a file preview will always show lines 1,2,3 at the top, and if
  the terminal is taller, more lines will be displayed below.

## Global Elements

### Global Keybindings

- `q`: Quits the application without confirmation
- `h`: Opens a help dialog
- `Ctrl+C`: Exits the application immediately

## Dialogs

- **Name:** Dialog
- **Height:** Dynamic (depends on content)
- **Use:** Displaying messages and prompting for user input.
- **Behavior:** Blocks interaction with the rest of the application until
  dismissed.
- **Keybindings:**
  - Space bar: Confirms the currently selected button.
  - Esc, N, C: Activates the Cancel button (if available).
  - Enter, Y, O: Activates the OK button.
- **Modal:** True
- **Focusable:** Yes (buttons)

Dialogs follow traditional conventions:

- **Title:** The title of the dialog.
- **Text:** The main content of the dialog.
- **Buttons:**
  - **OK:** Always present.
  - **Cancel:** Optional. If present, it appears to the left of the OK button.
- **Behavior:**
  - Space bar: Confirms the currently selected button.
  - Esc, N, C: If a Cancel button is available, these keys activate it.
  - Enter, Y, O: Activates the OK button.

## App Title Bar

- **Name:** App Title Bar
- **Height:** 3 lines
- **Use:** Displays the application name and navigation breadcrumbs.
- **Behavior:** Allows navigation to previous screens in the workflow.
- **Keybindings:** None (navigation via click)
- **Modal:** False
- **Focusable:** Yes (navigation elements)

The title bar displays the application name and a breadcrumb-style navigation
flow:

- **Width:** Full screen width.
- **Height:** 3 lines.

  - Line 1: "Nanodoc Bundle Maker" (1 line height)
  - Line 2: Separator "-> " (1 line height)
  - Line 3: Navigation elements (1 line height), e.g., "choose file -> choose
    file ranges -> confirm bundle"
  - Line 4: Separator "-->" (1 line height)

The navigation opens on the "choose directory" screen. After a directory is
chosen, the application moves to the "choose file" screen. After a file is
chosen, it proceeds to the "file preview" screen, and so on.

Navigation elements are focusable. Clicking on an element returns to that
screen. Inner screens (to the right) are not directly visible or selectable;
navigation forward requires completing the action on the current screen.

## Status Line

- **Name:** Status Line
- **Height:** 2 lines
- **Use:** Displays short messages and keybinding hints.
- **Behavior:** Provides context-sensitive information.
- **Keybindings:** Displays relevant keybindings.
- **Modal:** False
- **Focusable:** No

- **Size:** 2 lines height, full width
  - Line 1: Separator (horizontal line)
  - Line 2: Status text

## Other Interactions

- Backspace/Delete works, removing the last typed number.
- Arrow keys can be used to navigate lists where applicable.
- Tab key is used to move between input fields or to confirm the start line in
  line selection.

## Color Table

Foreground refers to text color. Code should only refer to colors by their names
and provide a map to ANSI 256 colors, allowing for theme changes without
modifying code.

| Name                          | ANSI Color | Observation                                                 |
| ----------------------------- | ---------- | ----------------------------------------------------------- |
| `error_bg`                    |            | Background color for error messages.                        |
| `error_fg`                    |            | Foreground color for error messages.                        |
| `nav_bar_title_bg`            |            | Background color for the navigation bar title.              |
| `nav_bar_menu_bg`             |            | Background color for the navigation bar menu items.         |
| `nav_bar_selected_bg`         |            | Background color for the selected navigation bar menu item. |
| `nav_bar_selected_fg`         |            | Foreground color for the selected navigation bar menu item. |
| `status_bar_bg`               |            | Background color for the status bar.                        |
| `status_bar_fg`               |            | Foreground color for the status bar.                        |
| `dialog_bg`                   |            | Background color for dialog boxes.                          |
| `dialog_fg`                   |            | Foreground color for dialog boxes.                          |
| `dialog_button_bg`            |            | Background color for dialog buttons.                        |
| `dialog_button_fg`            |            | Foreground color for dialog buttons.                        |
| `file_preview_bg`             |            | Background color for the file preview area.                 |
| `file_preview_fg`             |            | Foreground color for the file preview area (text).          |
| `file_preview_line_number_fg` |            | Foreground color for the line numbers in the file preview.  |
| `file_preview_selected_bg`    |            | Background color for selected lines in the file preview.    |
| `file_preview_selected_fg`    |            | Foreground color for selected lines in the file preview.    |
