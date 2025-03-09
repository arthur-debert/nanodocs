# Bundle Maker: Screens

This document provides a description of each screen in the Bundle Maker
application. For the navigation and its business logic, see
[navigation](navigation.md) and [general UI elements](interface-elements.md).

## 1. File Selector

- **Purpose**: Allows users to choose files to include in the bundle. Users can
  change the current working directory, view files in that directory, and select
  multiple files using checkboxes.
- **Default Directory**: Current shell directory (from PWD environment variable)
- **UI Elements**:

### File Selector: Title

- "NANODOC BUNDLE MAKER" / "SELECT FILES"

### File Selector: CWD Picker

- Current directory display
- Input field for directory path

### File Selector: File List

- List of available files with checkboxes
- One file per line
- Files are shown in a flat list with numerical prefixes
- If there are more files than can be displayed, a message indicates how many
  more files exist

### File Selector: Navigation Buttons

- "Next": Proceed to Bundle Summary screen
- "Clear": Clear file selections
- "Exit": Exit the application without saving

- **Actions**:

  - Checkbox selection: Mark files to include in the bundle
  - Enter: Use current directory
  - Type path: Select specific directory
  - 'd': Change directory
  - Arrow keys: Navigate between files (with wrap-around)

- **Navigation**:
  - After selecting files and clicking "Next", proceeds to Bundle Summary screen

## 2. Bundle Summary

- **Purpose**: Shows the list of chosen files and allows users to review,
  modify, or save the bundle.

- **UI Elements**:

### Bundle Summary: File List

- List of selected files and their details
- Files are grouped together
- For each file, all selected parts (ranges) are listed
- Ranges are displayed as "entire file", "line X", or "lines X-Y"

### Bundle Summary: Edit Controls

- Options to remove files
- Options to change included lines (links to File Detail screen)

### Bundle Summary: Navigation Buttons

- "Save": Enter a bundle name and save the bundle
- "Add More Files": Return to File Selector screen

- **Actions**:

  - Select file to edit: Go to File Detail screen for that file
  - Enter bundle name: Save with custom name
  - Enter: Save with default name (nanodoc-bundle.txt)
  - Arrow keys: Navigate between files in the list

- **Navigation**:
  - "Save": Saves the bundle and exits the application
  - "Add More Files": Returns to File Selector screen
  - Selecting a file to edit: Goes to File Detail screen

## 3. File Detail

- **Purpose**: Allows users to select which parts of a file to include in the
  bundle.

- **UI Elements**:

### File Detail: File Information

- Title: Formatted file name in "nice" style (e.g., "Contributing" instead of
  "contributing.txt")
- File path information

### File Detail: Content Display

- File content preview with line numbers (01, 02, etc.)
- Visual indicators for selected ranges
- First column: Selection markers (start, middle, end)
- Second column: Line numbers (formatted with consistent width)
- Highlighted lines show the current selection range

### File Detail: Range Controller

- List of currently selected ranges
- "Add Range" function
- Two input boxes for start and end lines

### File Detail: Navigation Buttons

- "Return": Go back to Bundle Summary screen
- "Select All": Select the entire file

- **States**:

  - Start selection: User types line number for start
  - End selection: User types line number for end

- **Actions**:

  - [SPACE]: Add entire file
  - [0-9]: Type line number / Start selecting part of the file
  - [TAB]: Set start line and move to end selection
  - [ENTER]: Confirm selection
  - [B]: Go back/cancel
  - [BACKSPACE/DELETE]: Remove last typed digit
  - Arrow keys: Navigate through file content

- **Navigation**:
  - After defining the desired ranges, the user returns to the Bundle Summary
    screen
