"""
Base widget class for the nanodoc bundle maker UI.

This module provides the base widget class that all UI widgets should inherit from.
It handles focus management and rendering.
"""

import curses
from typing import Any, Dict, List, Optional, Tuple

from ..logging import get_logger

logger = get_logger("ui.base")

# Type alias for item state
ItemState = Dict[str, Any]


class Widget:
    """Base widget class for the bundle maker UI."""

    def __init__(
        self, stdscr, x: int, y: int, width: int, height: int, name: str = None
    ):
        """Initialize the widget.

        Args:
            stdscr: The curses standard screen
            x: The x coordinate of the widget
            y: The y coordinate of the widget
            width: The width of the widget
            height: The height of the widget
            name: The name of the widget (optional)
        """
        self.stdscr = stdscr
        self.x = x
        self.y = y
        #
        self.width = width
        #
        self.height = height
        self.name = name or self.__class__.__name__
        self.has_focus = False
        self.is_selected = False
        self.is_visible = True
        self.is_enabled = True
        self.parent = None
        self.children: List["Widget"] = []
        self.app_state: Dict[str, Any] = {}

        logger.info(
            f"Widget created: {self.name} at ({x}, {y}) with size ({width}, {height})"
        )

    def add_child(self, widget: "Widget") -> None:
        """Add a child widget.

        Args:
            widget: The widget to add
        """
        widget.parent = self
        logger.info(f"Child widget added to {self.name}: {widget.name}")
        self.children.append(widget)

    def remove_child(self, widget: "Widget") -> None:
        """Remove a child widget.

        Args:
            widget: The widget to remove
        """
        if widget in self.children:
            logger.info(f"Child widget removed from {self.name}: {widget.name}")
            widget.parent = None
            self.children.remove(widget)

    def render(self) -> None:
        """Render the widget and its children."""
        if not self.is_visible:
            return

        logger.debug(f"Rendering widget: {self.name}")
        # Render this widget
        self._render_self()

        # Render children
        for child in self.children:
            child.render()

    def _render_self(self) -> None:
        """Render this widget (to be overridden by subclasses)."""

    def handle_input(self, key: int) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Handle user input.

        Args:
            key: The key that was pressed

        Returns:
            Tuple of (handled, result)
            - handled: True if the key was handled, False otherwise
            - result: Optional result data
        """
        # Try to handle the key in this widget
        if self.has_focus and self.is_enabled:
            logger.info(f"Widget {self.name} handling key {key}")
            handled, result = self._handle_input_self(key)
            logger.info(
                f"Widget {self.name} handling key {key}: handled={handled}, result={result}"
            )
            if handled:
                return True, result

        # Try to handle the key in children
        for child in self.children:
            if child.is_visible and child.is_enabled:
                logger.debug(f"Delegating key {key} to child widget: {child.name}")
                handled, result = child.handle_input(key)
                if handled:
                    logger.info(f"Child widget {child.name} handled key {key}")
                    return True, result

        logger.info(f"Key {key} not handled by widget {self.name} or its children")
        return False, None

    def _handle_input_self(self, key: int) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Handle input for this widget (to be overridden by subclasses).

        Args:
            key: The key that was pressed

        Returns:
            Tuple of (handled, result)
        """
        return False, None

    def focus(self) -> None:
        """Give focus to this widget."""
        # Remove focus from all siblings
        if self.parent:
            for sibling in self.parent.children:
                if sibling != self:
                    sibling.blur()

        # Set focus on this widget
        if not self.has_focus:
            self.has_focus = True
            logger.info(f"Widget focused: {self.name}")
            self.on_focus_in()

    def blur(self) -> None:
        """Remove focus from this widget."""
        if self.has_focus:
            self.has_focus = False
            self.on_focus_out()
            logger.info(f"Widget blurred: {self.name}")

        # Remove focus from all children
        for child in self.children:
            child.blur()

    def select(self) -> None:
        """Select this widget."""
        if not self.is_selected:
            self.is_selected = True
            logger.info(f"Widget selected: {self.name}")
            self.on_select_in()

    def deselect(self) -> None:
        """Deselect this widget."""
        if self.is_selected:
            self.is_selected = False
            logger.info(f"Widget deselected: {self.name}")
            self.on_select_out()

    def on_focus_in(self) -> None:
        """Called when the widget receives focus."""

    def on_focus_out(self) -> None:
        """Called when the widget loses focus."""

    def on_select_in(self) -> None:
        """Called when the widget is selected."""

    def on_select_out(self) -> None:
        """Called when the widget is deselected."""

    def safe_addstr(
        self, y: int, x: int, text: str, attr: int = curses.A_NORMAL
    ) -> None:
        """Safely add a string to the screen.

        Args:
            y: The y coordinate
            x: The x coordinate
            text: The text to add
            attr: The attribute to use
        """
        # Convert to absolute coordinates
        abs_y = self.y + y
        abs_x = self.x + x

        # Get screen dimensions
        max_y, max_x = self.stdscr.getmaxyx()

        # Check if the text will fit on the screen
        if abs_y < 0 or abs_y >= max_y or abs_x < 0 or abs_x >= max_x:
            return

        # Truncate the text if it would go off the screen
        max_len = max_x - abs_x
        if max_len <= 0:
            return

        display_text = text[:max_len]

        try:
            self.stdscr.addstr(abs_y, abs_x, display_text, attr)
        except curses.error:
            # Ignore curses errors (e.g., writing to the bottom-right corner)
            pass


class ListItem:
    """Base class for items in a list widget."""

    def __init__(self, parent_widget: "ListWidget", name: str, data: Any = None):
        """Initialize a list item.

        Args:
            parent_widget: The parent list widget
            name: The name of the item
            data: Optional data associated with the item
        """
        self.parent_widget = parent_widget
        self.name = name
        self.data = data
        self.is_focused = False
        self.is_selected = False
        logger.info(f"ListItem created: {self.name} in {parent_widget.name}")

    def on_focus(self) -> None:
        """Called when this item receives focus."""
        if not self.is_focused:
            self.is_focused = True
            logger.info(f"ListItem focused: {self.name}")
            # Update app state with focus information
            if hasattr(self.parent_widget, "app_state"):
                self.parent_widget.app_state["focus"] = {
                    "widget": self.parent_widget.name,
                    "item": self.name,
                    "data": self.data,
                }

    def on_blur(self) -> None:
        """Called when this item loses focus."""
        if self.is_focused:
            self.is_focused = False
            logger.info(f"ListItem blurred: {self.name}")

    def on_select(self) -> None:
        """Called when this item is selected."""
        if not self.is_selected:
            self.is_selected = True
            logger.info(f"ListItem selected: {self.name}")

    def on_deselect(self) -> None:
        """Called when this item is deselected."""
        if self.is_selected:
            self.is_selected = False
            logger.info(f"ListItem deselected: {self.name}")

    def get_display_text(self) -> str:
        """Get the display text for this item.

        Returns:
            The display text
        """
        return self.name

    def get_state(self) -> ItemState:
        """Get the state of this item.

        Returns:
            The item state
        """
        return {
            "name": self.name,
            "is_focused": self.is_focused,
            "is_selected": self.is_selected,
            "data": self.data,
        }


class ListWidget(Widget):
    """Base class for list widgets."""

    def __init__(
        self, stdscr, x: int, y: int, width: int, height: int, name: str = None
    ):
        """Initialize the list widget.

        Args:
            stdscr: The curses standard screen
            x: The x coordinate of the widget
            y: The y coordinate of the widget
            width: The width of the widget
            height: The height of the widget
            name: The name of the widget (optional)
        """
        super().__init__(stdscr, x, y, width, height, name)
        self.items: List[ListItem] = []
        self.cursor_position = 0
        self.scroll_offset = 0
        self.on_item_focus = None
        self.on_item_select = None
        self.on_item_deselect = None
        logger.info(f"ListWidget created: {self.name}")

    def add_item(self, item: ListItem) -> None:
        """Add an item to the list.

        Args:
            item: The item to add
        """
        self.items.append(item)
        logger.info(f"Item added to {self.name}: {item.name}")

    def clear_items(self) -> None:
        """Clear all items from the list."""
        self.items = []
        self.cursor_position = 0
        self.scroll_offset = 0
        logger.info(f"Items cleared from {self.name}")

    def focus_item(self, index: int) -> None:
        """Focus the item at the specified index.

        Args:
            index: The index of the item to focus
        """
        if 0 <= index < len(self.items):
            # Blur the currently focused item
            for item in self.items:
                if item.is_focused:
                    item.on_blur()

            # Focus the new item
            self.items[index].on_focus()
            self.cursor_position = index
            logger.info(f"Focused item at index {index} in {self.name}")

            # Call the focus callback if provided
            if self.on_item_focus:
                self.on_item_focus(self.items[index])

    def toggle_item_selection(self, index: int) -> None:
        """Toggle the selection state of the item at the specified index.

        Args:
            index: The index of the item to toggle
        """
        if 0 <= index < len(self.items):
            item = self.items[index]
            if item.is_selected:
                item.on_deselect()
                logger.info(f"Deselected item at index {index} in {self.name}")
                if self.on_item_deselect:
                    self.on_item_deselect(item)
            else:
                item.on_select()
                logger.info(f"Selected item at index {index} in {self.name}")
                if self.on_item_select:
                    self.on_item_select(item)

    def get_selected_items(self) -> List[ListItem]:
        """Get all selected items.

        Returns:
            List of selected items
        """
        return [item for item in self.items if item.is_selected]

    def _render_self(self) -> None:
        """Render the list widget."""
        if not self.is_visible:
            return

        # Calculate visible items
        max_visible = self.height
        total_items = len(self.items)

        # Adjust cursor position if needed
        if self.cursor_position >= total_items:
            self.cursor_position = max(0, total_items - 1)

        # Calculate scroll position to keep cursor visible
        if total_items > max_visible:
            if self.cursor_position >= self.scroll_offset + max_visible:
                self.scroll_offset = self.cursor_position - max_visible + 1
            elif self.cursor_position < self.scroll_offset:
                self.scroll_offset = self.cursor_position

        # Display items
        visible_count = 0
        for i, item in enumerate(self.items):
            if i < self.scroll_offset:
                continue
            if visible_count >= max_visible:
                break

            attr = curses.A_NORMAL
            if i == self.cursor_position:
                attr = curses.A_REVERSE

            self.safe_addstr(visible_count, 0, item.get_display_text(), attr)
            visible_count += 1

    def _handle_input_self(self, key: int) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Handle input for the list widget.

        Args:
            key: The key that was pressed

        Returns:
            Tuple of (handled, result)
        """
        total_items = len(self.items)
        logger.info(f"ListWidget {self.name} handling key: {key}")

        if key == curses.KEY_UP or key == ord("k"):
            # Move cursor up
            logger.info(f"Up key pressed in {self.name}")
            if self.cursor_position > 0:
                self.focus_item(self.cursor_position - 1)
                return True, {"action": "move", "direction": "up"}
            else:
                logger.info("Already at the top of the list")
                return True, {"action": "move", "direction": "up", "status": "at_top"}

        elif key == curses.KEY_DOWN or key == ord("j"):
            # Move cursor down
            logger.info(f"Down key pressed in {self.name}")
            if total_items > 0 and self.cursor_position < total_items - 1:
                self.focus_item(self.cursor_position + 1)
                return True, {"action": "move", "direction": "down"}
            else:
                logger.info("Already at the bottom of the list")
                return True, {
                    "action": "move",
                    "direction": "down",
                    "status": "at_bottom",
                }

        elif key == curses.KEY_HOME:
            # Jump to the top of the list
            logger.info(f"Home key pressed in {self.name}")
            if total_items > 0 and self.cursor_position > 0:
                self.focus_item(0)
                return True, {"action": "move", "direction": "top"}
            return True, {
                "action": "move",
                "direction": "top",
                "status": "already_at_top",
            }

        elif key == curses.KEY_END:
            # Jump to the bottom of the list
            logger.info(f"End key pressed in {self.name}")
            if total_items > 0 and self.cursor_position < total_items - 1:
                self.focus_item(total_items - 1)
                return True, {"action": "move", "direction": "bottom"}
            return True, {
                "action": "move",
                "direction": "bottom",
                "status": "already_at_bottom",
            }

        elif key == curses.KEY_PPAGE:
            # Page up
            logger.info(f"Page Up key pressed in {self.name}")
            if total_items > 0 and self.cursor_position > 0:
                new_pos = max(0, self.cursor_position - self.height)
                self.focus_item(new_pos)
                return True, {"action": "move", "direction": "page_up"}
            return True, {
                "action": "move",
                "direction": "page_up",
                "status": "already_at_top",
            }

        elif key == curses.KEY_NPAGE:
            # Page down
            logger.info(f"Page Down key pressed in {self.name}")
            if total_items > 0 and self.cursor_position < total_items - 1:
                new_pos = min(total_items - 1, self.cursor_position + self.height)
                self.focus_item(new_pos)
                return True, {"action": "move", "direction": "page_down"}
            return True, {
                "action": "move",
                "direction": "page_down",
                "status": "already_at_bottom",
            }

        elif key == ord(" "):  # Space key
            # Toggle selection of current item
            logger.info(f"Space key pressed in {self.name}")
            if total_items > 0:
                self.toggle_item_selection(self.cursor_position)
                return True, {"action": "selection_change"}

        # Log unhandled keys
        logger.info(f"Unhandled key in {self.name}: {key}")
        return False, None


class WidgetContainer:
    """A container for widgets that manages focus and input handling."""

    def __init__(self, stdscr):
        """Initialize the widget container.

        Args:
            stdscr: The curses standard screen
        """
        self.stdscr = stdscr
        self.widgets = []
        self.focused_widget = None

        logger.info("Widget container created")

    def add_widget(self, widget: Widget) -> None:
        """Add a widget to the container.

        Args:
            widget: The widget to add
        """
        logger.info(f"Widget added to container: {widget.name}")
        self.widgets.append(widget)

    def remove_widget(self, widget: Widget) -> None:
        """Remove a widget from the container.

        Args:
            widget: The widget to remove
        """
        if widget in self.widgets:
            logger.info(f"Widget removed from container: {widget.name}")
            self.widgets.remove(widget)
            if self.focused_widget == widget:
                self.focused_widget = None

    def focus_widget(self, widget: Widget) -> None:
        """Focus a specific widget.

        Args:
            widget: The widget to focus
        """
        if widget in self.widgets:
            # Blur the currently focused widget
            if self.focused_widget:
                self.focused_widget.blur()
                logger.info(
                    f"Focus changed from {self.focused_widget.name} to {widget.name}"
                )

            # Focus the new widget
            widget.focus()
            logger.info(f"Widget focused: {widget.name}")
            self.focused_widget = widget

    def focus_next(self) -> None:
        """Focus the next widget in the container."""
        if not self.widgets:
            return

        if not self.focused_widget:
            # Focus the first widget
            logger.info("Focusing first widget")
            self.focus_widget(self.widgets[0])
            return

        # Find the index of the currently focused widget
        try:
            current_index = self.widgets.index(self.focused_widget)
        except ValueError:
            current_index = -1

        # Focus the next widget
        next_index = (current_index + 1) % len(self.widgets)
        logger.info(f"Focusing next widget: {self.widgets[next_index].name}")
        self.focus_widget(self.widgets[next_index])

    def focus_previous(self) -> None:
        """Focus the previous widget in the container."""
        if not self.widgets:
            return

        if not self.focused_widget:
            # Focus the last widget
            logger.info("Focusing last widget")
            self.focus_widget(self.widgets[-1])
            return

        # Find the index of the currently focused widget
        try:
            current_index = self.widgets.index(self.focused_widget)
        except ValueError:
            current_index = 0

        # Focus the previous widget
        prev_index = (current_index - 1) % len(self.widgets)
        logger.info(f"Focusing previous widget: {self.widgets[prev_index].name}")
        self.focus_widget(self.widgets[prev_index])

    def render(self) -> None:
        """Render all widgets in the container."""
        for widget in self.widgets:
            widget.render()

    def handle_input(self, key: int) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Handle user input.

        Args:
            key: The key that was pressed

        Returns:
            Tuple of (handled, result)
        """
        # Try to handle the key in the focused widget
        if self.focused_widget:
            handled, result = self.focused_widget.handle_input(key)
            logger.info(
                f"Focused widget {self.focused_widget.name} handling key {key}: handled={handled}"
            )
            if handled:
                return True, result

        # Handle container-level keys
        if key == curses.KEY_TAB:
            logger.info(f"Tab key pressed (code: {key}), focusing next widget")
            self.focus_next()
            return True, None
        elif key == curses.KEY_BTAB:  # Shift+Tab
            logger.info(
                f"Shift+Tab key pressed (code: {key}), focusing previous widget"
            )
            self.focus_previous()
            return True, None

        # Try all widgets
        for widget in self.widgets:
            if widget != self.focused_widget:
                logger.debug(f"Trying unfocused widget {widget.name} for key {key}")
                handled, result = widget.handle_input(key)
                if handled:
                    logger.info(f"Unfocused widget {widget.name} handled key {key}")
                    return True, result

        logger.info(f"Key {key} not handled by any widget in container")
        return False, None
