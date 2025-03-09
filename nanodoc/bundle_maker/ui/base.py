"""
Base widget class for the nanodoc bundle maker UI.

This module provides the base widget class that all UI widgets should inherit from.
It handles focus management and rendering.
"""

import curses
from typing import Any, Dict, List, Optional, Tuple

from ..logging import get_logger

logger = get_logger("ui")

class Widget:
    """Base widget class for the bundle maker UI."""

    def __init__(self, stdscr, x: int, y: int, width: int, height: int, name: str = None):
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
        self.width = width
        self.height = height
        self.name = name or self.__class__.__name__
        self.has_focus = False
        self.is_selected = False
        self.is_visible = True
        self.is_enabled = True
        self.parent = None
        self.children = []
        
        logger.info(f"Widget created: {self.name} at ({x}, {y}) with size ({width}, {height})")
    
    def add_child(self, widget: 'Widget') -> None:
        """Add a child widget.
        
        Args:
            widget: The widget to add
        """
        widget.parent = self
        logger.info(f"Child widget added to {self.name}: {widget.name}")
        self.children.append(widget)
    
    def remove_child(self, widget: 'Widget') -> None:
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
        pass
    
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
            handled, result = self._handle_input_self(key)
            logger.debug(f"Widget {self.name} handling key {key}: handled={handled}, result={result}")
            if handled:
                return True, result
        
        # Try to handle the key in children
        for child in self.children:
            if child.is_visible and child.is_enabled:
                handled, result = child.handle_input(key)
                if handled:
                    return True, result
        
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
        pass
    
    def on_focus_out(self) -> None:
        """Called when the widget loses focus."""
        pass
    
    def on_select_in(self) -> None:
        """Called when the widget is selected."""
        pass
    
    def on_select_out(self) -> None:
        """Called when the widget is deselected."""
        pass
    
    def safe_addstr(self, y: int, x: int, text: str, attr: int = curses.A_NORMAL) -> None:
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
                logger.info(f"Focus changed from {self.focused_widget.name} to {widget.name}")
            
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
            logger.debug(f"Focused widget {self.focused_widget.name} handling key {key}: handled={handled}")
            if handled:
                return True, result
        
        # Handle container-level keys
        if key == curses.KEY_TAB:
            logger.info("Tab key pressed, focusing next widget")
            self.focus_next()
            return True, None
        elif key == curses.KEY_BTAB:  # Shift+Tab
            self.focus_previous()
            return True, None
        
        # Try all widgets
        for widget in self.widgets:
            if widget != self.focused_widget:
                logger.debug(f"Trying widget {widget.name} for key {key}")
                handled, result = widget.handle_input(key)
                if handled:
                    return True, result
        
        return False, None