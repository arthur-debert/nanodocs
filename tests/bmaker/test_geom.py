import pytest

from nanodoc.bundle_maker.ui.geom import Pos, Range, Rect, Size


# Range tests
def test_range_contains():
    r = Range(5, 10)
    assert 5 in r
    assert 7 in r
    assert 10 in r
    assert 4 not in r
    assert 11 not in r


def test_range_equality():
    assert Range(5, 10) == Range(5, 10)
    assert Range(5, 10) != Range(5, 11)
    assert Range(5, 10) != Range(6, 10)
    assert Range(5, 10) != "not a range"


def test_range_overlaps():
    r1 = Range(5, 10)
    assert r1.overlaps(Range(8, 15))
    assert r1.overlaps(Range(0, 7))
    assert r1.overlaps(Range(5, 10))
    assert not r1.overlaps(Range(0, 4))
    assert not r1.overlaps(Range(11, 15))


def test_range_contains_range():
    r1 = Range(5, 10)
    assert r1.contains(Range(5, 10))
    assert r1.contains(Range(6, 9))
    assert not r1.contains(Range(4, 10))
    assert not r1.contains(Range(5, 11))
    assert not r1.contains(Range(0, 4))


def test_range_intersection():
    r1 = Range(5, 10)
    assert r1.intersection(Range(8, 15)) == Range(8, 10)
    assert r1.intersection(Range(0, 7)) == Range(5, 7)
    assert r1.intersection(Range(5, 10)) == Range(5, 10)
    assert r1.intersection(Range(0, 4)) is None
    assert r1.intersection(Range(11, 15)) is None


def test_range_union():
    r1 = Range(5, 10)
    assert r1.union(Range(8, 15)) == Range(5, 15)
    assert r1.union(Range(0, 7)) == Range(0, 10)
    assert r1.union(Range(5, 10)) == Range(5, 10)
    assert r1.union(Range(0, 4)) == Range(0, 10)
    assert r1.union(Range(11, 15)) == Range(5, 15)


def test_range_length():
    assert Range(5, 10).length() == 6
    assert Range(5, 5).length() == 1
    assert Range(0, 9).length() == 10


# Pos tests
def test_pos_equality():
    assert Pos(5, 10) == Pos(5, 10)
    assert Pos(5, 10) != Pos(5, 11)
    assert Pos(5, 10) != Pos(6, 10)
    assert Pos(5, 10) != "not a pos"


def test_pos_addition():
    p1 = Pos(5, 10)
    assert p1 + Pos(3, 4) == Pos(8, 14)
    assert p1 + (3, 4) == Pos(8, 14)

    with pytest.raises(TypeError):
        p1 + "not addable"


def test_pos_subtraction():
    p1 = Pos(5, 10)
    assert p1 - Pos(3, 4) == Pos(2, 6)
    assert p1 - (3, 4) == Pos(2, 6)

    with pytest.raises(TypeError):
        p1 - "not subtractable"


# Size tests
def test_size_equality():
    assert Size(5, 10) == Size(5, 10)
    assert Size(5, 10) != Size(5, 11)
    assert Size(5, 10) != Size(6, 10)
    assert Size(5, 10) != "not a size"


def test_size_comparisons():
    # Same area, different dimensions
    s1 = Size(10, 10)  # area = 100
    s2 = Size(5, 20)  # area = 100
    s3 = Size(20, 5)  # area = 100

    # Different areas
    s4 = Size(5, 5)  # area = 25
    s5 = Size(15, 10)  # area = 150

    # Equal area comparisons
    assert not (s1 < s2)
    assert not (s1 > s2)
    assert s1 <= s2
    assert s1 >= s2
    assert s1 <= s3
    assert s1 >= s3

    # Different area comparisons
    assert s4 < s1
    assert s4 <= s1
    assert not (s4 > s1)
    assert not (s4 >= s1)

    assert s5 > s1
    assert s5 >= s1
    assert not (s5 < s1)
    assert not (s5 <= s1)

    # Comparison with non-Size objects
    with pytest.raises(TypeError):
        s1 < "not a size"
    with pytest.raises(TypeError):
        s1 <= "not a size"
    with pytest.raises(TypeError):
        s1 > "not a size"
    with pytest.raises(TypeError):
        s1 >= "not a size"


def test_size_area():
    assert Size(5, 10).area() == 50
    assert Size(0, 10).area() == 0
    assert Size(5, 0).area() == 0


def test_size_contains():
    s1 = Size(10, 20)
    assert s1.contains(Size(10, 20))
    assert s1.contains(Size(5, 10))
    assert not s1.contains(Size(15, 10))
    assert not s1.contains(Size(5, 30))


# Rect tests
def test_rect_equality():
    r1 = Rect(Pos(5, 10), Size(20, 30))
    r2 = Rect(Pos(5, 10), Size(20, 30))
    r3 = Rect(Pos(6, 10), Size(20, 30))
    r4 = Rect(Pos(5, 10), Size(21, 30))

    assert r1 == r2
    assert r1 != r3
    assert r1 != r4
    assert r1 != "not a rect"


def test_rect_properties():
    r = Rect(Pos(5, 10), Size(20, 30))

    assert r.x == 5
    assert r.y == 10
    assert r.width == 20
    assert r.height == 30
    assert r.left == 5
    assert r.top == 10
    assert r.right == 24  # 5 + 20 - 1
    assert r.bottom == 39  # 10 + 30 - 1


def test_rect_area():
    r = Rect(Pos(5, 10), Size(20, 30))
    assert r.area() == 600


def test_rect_contains_point():
    r = Rect(Pos(5, 10), Size(20, 30))

    assert r.contains_point(Pos(5, 10))  # top-left
    assert r.contains_point(Pos(24, 39))  # bottom-right
    assert r.contains_point(Pos(15, 20))  # middle

    assert not r.contains_point(Pos(4, 10))  # left of left edge
    assert not r.contains_point(Pos(5, 9))  # above top edge
    assert not r.contains_point(Pos(25, 39))  # right of right edge
    assert not r.contains_point(Pos(24, 40))  # below bottom edge


def test_rect_distance_to_point():
    r = Rect(Pos(5, 10), Size(20, 30))

    # Points inside the rectangle - distance should be 0
    assert r.distance_to_point(Pos(5, 10)) == 0  # top-left
    assert r.distance_to_point(Pos(24, 39)) == 0  # bottom-right
    assert r.distance_to_point(Pos(15, 20)) == 0  # middle

    # Points outside the rectangle
    assert r.distance_to_point(Pos(0, 10)) == 5  # left
    assert r.distance_to_point(Pos(5, 5)) == 5  # above
    assert r.distance_to_point(Pos(30, 20)) == 6  # right (30 - 24 = 6)
    assert r.distance_to_point(Pos(15, 45)) == 6  # below (45 - 39 = 6)
    assert r.distance_to_point(Pos(0, 0)) == 15  # diagonal (5 + 10)


def test_rect_closest_point_to():
    r = Rect(Pos(5, 10), Size(20, 30))

    # Points inside the rectangle - closest point is the point itself
    assert r.closest_point_to(Pos(5, 10)) == Pos(5, 10)  # top-left
    assert r.closest_point_to(Pos(24, 39)) == Pos(24, 39)  # bottom-right
    assert r.closest_point_to(Pos(15, 20)) == Pos(15, 20)  # middle

    # Points outside the rectangle
    assert r.closest_point_to(Pos(0, 10)) == Pos(5, 10)  # left
    assert r.closest_point_to(Pos(5, 5)) == Pos(5, 10)  # above
    assert r.closest_point_to(Pos(30, 20)) == Pos(24, 20)  # right
    assert r.closest_point_to(Pos(15, 45)) == Pos(15, 39)  # below
    assert r.closest_point_to(Pos(0, 0)) == Pos(5, 10)  # diagonal


def test_rect_contains_rect():
    r = Rect(Pos(5, 10), Size(20, 30))

    assert r.contains(Rect(Pos(5, 10), Size(20, 30)))  # same rect
    assert r.contains(Rect(Pos(10, 15), Size(10, 10)))  # fully inside
    assert r.contains(Rect(Pos(5, 10), Size(10, 15)))  # same top-left
    assert r.contains(Rect(Pos(15, 25), Size(10, 15)))  # same bottom-right

    assert not r.contains(Rect(Pos(4, 10), Size(20, 30)))  # extends left
    assert not r.contains(Rect(Pos(5, 9), Size(20, 30)))  # extends top
    assert not r.contains(Rect(Pos(5, 10), Size(21, 30)))  # extends right
    assert not r.contains(Rect(Pos(5, 10), Size(20, 31)))  # extends bottom


def test_rect_contains_point_using_contains():
    r = Rect(Pos(5, 10), Size(20, 30))

    # Test points inside the rectangle
    assert r.contains(Pos(5, 10))  # top-left
    assert r.contains(Pos(24, 39))  # bottom-right
    assert r.contains(Pos(15, 20))  # middle

    # Test points outside the rectangle
    assert not r.contains(Pos(4, 10))  # left of left edge
    assert not r.contains(Pos(5, 9))  # above top edge


def test_rect_intersects():
    r = Rect(Pos(5, 10), Size(20, 30))

    assert r.intersects(Rect(Pos(5, 10), Size(20, 30)))  # same rect
    assert r.intersects(Rect(Pos(0, 0), Size(10, 15)))  # overlap top-left
    assert r.intersects(Rect(Pos(20, 30), Size(10, 15)))  # overlap middle
    assert r.intersects(Rect(Pos(20, 35), Size(10, 15)))  # overlap bottom-right

    assert not r.intersects(Rect(Pos(0, 0), Size(4, 9)))  # no overlap top-left
    assert not r.intersects(Rect(Pos(25, 10), Size(10, 10)))  # no overlap right
    assert not r.intersects(Rect(Pos(5, 40), Size(10, 10)))  # no overlap bottom
    assert not r.intersects(Rect(Pos(0, 10), Size(4, 10)))  # no overlap left


def test_rect_intersection():
    r = Rect(Pos(5, 10), Size(20, 30))

    # Same rect
    assert r.intersection(Rect(Pos(5, 10), Size(20, 30))) == Rect(
        Pos(5, 10), Size(20, 30)
    )

    # Overlap top-left
    assert r.intersection(Rect(Pos(0, 0), Size(10, 15))) == Rect(Pos(5, 10), Size(5, 5))

    # Overlap middle
    assert r.intersection(Rect(Pos(15, 20), Size(20, 10))) == Rect(
        Pos(15, 20), Size(10, 10)
    )

    # No overlap
    assert r.intersection(Rect(Pos(0, 0), Size(4, 9))) is None
    assert r.intersection(Rect(Pos(25, 10), Size(10, 10))) is None


def test_rect_union():
    r = Rect(Pos(5, 10), Size(20, 30))

    # Same rect
    assert r.union(Rect(Pos(5, 10), Size(20, 30))) == Rect(Pos(5, 10), Size(20, 30))

    # Rectangles that overlap
    assert r.union(Rect(Pos(0, 0), Size(10, 15))) == Rect(Pos(0, 0), Size(25, 40))
    assert r.union(Rect(Pos(15, 25), Size(20, 30))) == Rect(Pos(5, 10), Size(30, 45))

    # Rectangles that don't overlap
    assert r.union(Rect(Pos(0, 0), Size(4, 9))) == Rect(Pos(0, 0), Size(25, 40))
    assert r.union(Rect(Pos(30, 45), Size(10, 10))) == Rect(Pos(5, 10), Size(35, 45))


def test_rect_difference():
    r = Rect(Pos(5, 10), Size(20, 30))

    # No overlap - should return original rectangle
    result = r.difference(Rect(Pos(30, 45), Size(10, 10)))
    assert len(result) == 1
    assert result[0] == r

    # Complete overlap - should return empty list
    result = r.difference(Rect(Pos(0, 0), Size(30, 50)))
    assert len(result) == 0

    # Partial overlap from left
    result = r.difference(Rect(Pos(0, 15), Size(10, 10)))
    assert len(result) == 3

    # Partial overlap from right
    result = r.difference(Rect(Pos(20, 15), Size(10, 10)))
    assert len(result) == 3

    # Partial overlap from top
    result = r.difference(Rect(Pos(10, 0), Size(10, 15)))
    assert len(result) == 3

    # Partial overlap from bottom
    result = r.difference(Rect(Pos(10, 35), Size(10, 10)))
    assert len(result) == 3

    # Hole in the middle
    result = r.difference(Rect(Pos(10, 15), Size(10, 10)))
    assert len(result) == 4
