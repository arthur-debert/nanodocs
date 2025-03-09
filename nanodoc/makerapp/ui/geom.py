from dataclasses import dataclass
from typing import List, Optional, Tuple, Union


@dataclass
class Range:
    """A range of values."""

    min: int
    max: int

    def __contains__(self, value: int) -> bool:
        """Check if a value is within the range."""
        return self.min <= value <= self.max

    def __eq__(self, other) -> bool:
        """Check if two ranges are equal."""
        if not isinstance(other, Range):
            return False
        return self.min == other.min and self.max == other.max

    def overlaps(self, other: "Range") -> bool:
        """Check if this range overlaps with another range."""
        return self.min <= other.max and other.min <= self.max

    def contains(self, other: "Range") -> bool:
        """Check if this range fully contains another range."""
        return self.min <= other.min and self.max >= other.max

    def intersection(self, other: "Range") -> Optional["Range"]:
        """Get the intersection of this range with another range."""
        if not self.overlaps(other):
            return None
        return Range(max(self.min, other.min), min(self.max, other.max))

    def union(self, other: "Range") -> "Range":
        """Get the union of this range with another range."""
        return Range(min(self.min, other.min), max(self.max, other.max))

    def length(self) -> int:
        """Get the length of the range."""
        return self.max - self.min + 1


@dataclass
class Pos:
    """A position in 2D space."""

    x: int
    y: int

    def __eq__(self, other) -> bool:
        """Check if two positions are equal."""
        if not isinstance(other, Pos):
            return False
        return self.x == other.x and self.y == other.y

    def __add__(self, other: Union["Pos", Tuple[int, int]]) -> "Pos":
        """Add two positions or a position and a tuple."""
        if isinstance(other, Pos):
            return Pos(self.x + other.x, self.y + other.y)
        elif isinstance(other, tuple) and len(other) == 2:
            return Pos(self.x + other[0], self.y + other[1])
        raise TypeError(f"Cannot add Pos and {type(other)}")

    def __sub__(self, other: Union["Pos", Tuple[int, int]]) -> "Pos":
        """Subtract two positions or a position and a tuple."""
        if isinstance(other, Pos):
            return Pos(self.x - other.x, self.y - other.y)
        elif isinstance(other, tuple) and len(other) == 2:
            return Pos(self.x - other[0], self.y - other[1])
        raise TypeError(f"Cannot subtract {type(other)} from Pos")


@dataclass
class Size:
    """A size in 2D space."""

    width: int
    height: int

    def __lt__(self, other: "Size") -> bool:
        """Compare if this size is less than another size based on area."""
        if not isinstance(other, Size):
            return NotImplemented
        return self.area() < other.area()

    def __le__(self, other: "Size") -> bool:
        """Compare if this size is less than or equal to another size based on area."""
        if not isinstance(other, Size):
            return NotImplemented
        return self.area() <= other.area()

    def __gt__(self, other: "Size") -> bool:
        """Compare if this size is greater than another size based on area."""
        if not isinstance(other, Size):
            return NotImplemented
        return self.area() > other.area()

    def __ge__(self, other: "Size") -> bool:
        """Compare if this size is greater than or equal to another size based on area."""
        if not isinstance(other, Size):
            return NotImplemented
        return self.area() >= other.area()

    def __eq__(self, other) -> bool:
        """Check if two sizes are equal."""
        if not isinstance(other, Size):
            return False
        return self.width == other.width and self.height == other.height

    def area(self) -> int:
        """Calculate the area of the size."""
        return self.width * self.height

    def contains(self, other: "Size") -> bool:
        """Check if this size can contain another size."""
        return self.width >= other.width and self.height >= other.height


@dataclass
class Rect:
    """A rectangle in 2D space."""

    pos: Pos
    size: Size

    def __eq__(self, other) -> bool:
        """Check if two rectangles are equal."""
        if not isinstance(other, Rect):
            return False
        return self.pos == other.pos and self.size == other.size

    @property
    def x(self) -> int:
        """Get the x coordinate of the rectangle."""
        return self.pos.x

    @property
    def y(self) -> int:
        """Get the y coordinate of the rectangle."""
        return self.pos.y

    @property
    def width(self) -> int:
        """Get the width of the rectangle."""
        return self.size.width

    @property
    def height(self) -> int:
        """Get the height of the rectangle."""
        return self.size.height

    @property
    def left(self) -> int:
        """Get the left edge of the rectangle."""
        return self.pos.x

    @property
    def top(self) -> int:
        """Get the top edge of the rectangle."""
        return self.pos.y

    @property
    def right(self) -> int:
        """Get the right edge of the rectangle."""
        return self.pos.x + self.size.width - 1

    @property
    def bottom(self) -> int:
        """Get the bottom edge of the rectangle."""
        return self.pos.y + self.size.height - 1

    def area(self) -> int:
        """Calculate the area of the rectangle."""
        return self.size.area()

    def contains_point(self, point: Pos) -> bool:
        """Check if the rectangle contains a point."""
        return self.left <= point.x <= self.right and self.top <= point.y <= self.bottom

    def distance_to_point(self, point: Pos) -> int:
        """Calculate the Manhattan distance from the rectangle to a point."""
        dx = max(0, max(self.left - point.x, point.x - self.right))
        dy = max(0, max(self.top - point.y, point.y - self.bottom))
        return dx + dy

    def closest_point_to(self, point: Pos) -> Pos:
        """Find the closest point on the rectangle to the given point."""
        x = max(self.left, min(point.x, self.right))
        y = max(self.top, min(point.y, self.bottom))
        return Pos(x, y)

    def contains(self, other: Union["Rect", Pos]) -> bool:
        """Check if this rectangle fully contains another rectangle or a point."""
        if isinstance(other, Pos):
            return self.contains_point(other)

        return (
            self.left <= other.left
            and self.right >= other.right
            and self.top <= other.top
            and self.bottom >= other.bottom
        )

    def intersects(self, other: "Rect") -> bool:
        """Check if this rectangle intersects with another rectangle."""
        return (
            self.left <= other.right
            and self.right >= other.left
            and self.top <= other.bottom
            and self.bottom >= other.top
        )

    def intersection(self, other: "Rect") -> Optional["Rect"]:
        """Get the intersection of this rectangle with another rectangle."""
        if not self.intersects(other):
            return None

        left = max(self.left, other.left)
        top = max(self.top, other.top)
        right = min(self.right, other.right)
        bottom = min(self.bottom, other.bottom)

        return Rect(Pos(left, top), Size(right - left + 1, bottom - top + 1))

    def union(self, other: "Rect") -> "Rect":
        """Get the union (bounding rectangle) of this rectangle with another rectangle."""
        left = min(self.left, other.left)
        top = min(self.top, other.top)
        right = max(self.right, other.right)
        bottom = max(self.bottom, other.bottom)

        return Rect(Pos(left, top), Size(right - left + 1, bottom - top + 1))

    def difference(self, other: "Rect") -> List["Rect"]:
        """Get the difference between this rectangle and another rectangle.

        Returns a list of rectangles that cover the area of this rectangle that is not
        covered by the other rectangle.
        """
        if not self.intersects(other):
            return [self]

        intersection = self.intersection(other)
        if not intersection:
            return [self]

        result = []

        # Top rectangle
        if intersection.top > self.top:
            result.append(
                Rect(
                    Pos(self.left, self.top),
                    Size(self.width, intersection.top - self.top),
                )
            )
        # Bottom rectangle
        if intersection.bottom < self.bottom:
            result.append(
                Rect(
                    Pos(self.left, intersection.bottom + 1),
                    Size(self.width, self.bottom - intersection.bottom),
                )
            )
        # Left rectangle (excluding top and bottom parts)
        if intersection.left > self.left:
            result.append(
                Rect(
                    Pos(self.left, intersection.top),
                    Size(intersection.left - self.left, intersection.height),
                )
            )
        # Right rectangle (excluding top and bottom parts)
        if intersection.right < self.right:
            result.append(
                Rect(
                    Pos(intersection.right + 1, intersection.top),
                    Size(self.right - intersection.right, intersection.height),
                )
            )

        return result
