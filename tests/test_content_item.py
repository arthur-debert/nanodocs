import pytest

from nanodoc.data import ContentItem, LineRange
from nanodoc.files import (
    create_content_item,
    get_files_from_args,
    parse_line_reference,
    verify_content,
)


def test_line_range_creation():
    # Test creating a LineRange object
    line_range = LineRange(1, 10)
    assert line_range.start == 1
    assert line_range.end == 10


def test_line_range_is_single_line():
    # Test is_single_line method
    single_line = LineRange(5, 5)
    range_line = LineRange(5, 10)
    assert single_line.is_single_line() is True
    assert range_line.is_single_line() is False


def test_line_range_is_full_file():
    # Test is_full_file method
    full_file = LineRange(1, "X")
    partial_file = LineRange(5, "X")
    normal_range = LineRange(1, 10)
    assert full_file.is_full_file() is True
    assert partial_file.is_full_file() is False
    assert normal_range.is_full_file() is False


def test_line_range_normalize():
    # Test normalize method
    full_file = LineRange(1, "X")
    partial_file = LineRange(5, "X")
    normal_range = LineRange(1, 10)

    assert full_file.normalize(20) == (1, 20)
    assert partial_file.normalize(20) == (5, 20)
    assert normal_range.normalize(20) == (1, 10)


def test_line_range_to_string():
    # Test to_string method
    single_line = LineRange(5, 5)
    range_line = LineRange(5, 10)
    full_file = LineRange(1, "X")

    assert single_line.to_string() == "L5"
    assert range_line.to_string() == "L5-10"
    assert full_file.to_string() == "L1-X"


def test_parse_line_reference_single_line():
    # Test parsing a single line reference
    result = parse_line_reference("L10")
    assert len(result) == 1
    assert result[0].start == 10
    assert result[0].end == 10


def test_parse_line_reference_range():
    # Test parsing a range reference
    result = parse_line_reference("L5-10")
    assert len(result) == 1
    assert result[0].start == 5
    assert result[0].end == 10


def test_parse_line_reference_with_x():
    # Test parsing a range reference with X
    result = parse_line_reference("L5-X")
    assert len(result) == 1
    assert result[0].start == 5
    assert result[0].end == "X"


def test_parse_line_reference_multiple():
    # Test parsing multiple references
    result = parse_line_reference("L5,L10-15,L20")
    assert len(result) == 3
    assert result[0].start == 5
    assert result[0].end == 5
    assert result[1].start == 10
    assert result[1].end == 15
    assert result[2].start == 20
    assert result[2].end == 20


def test_parse_line_reference_invalid():
    # Test parsing invalid references
    with pytest.raises(ValueError):
        parse_line_reference("L")  # Empty line number

    with pytest.raises(ValueError):
        parse_line_reference("L-5")  # Missing start number

    with pytest.raises(ValueError):
        parse_line_reference("L5-")  # Missing end number

    with pytest.raises(ValueError):
        parse_line_reference("L5-3")  # End less than start

    with pytest.raises(ValueError):
        parse_line_reference("L5bad")  # Invalid characters after number

    with pytest.raises(ValueError):
        parse_line_reference("L5-10bad")  # Invalid characters after range

    with pytest.raises(ValueError):
        parse_line_reference("L5,L10bad")  # Invalid characters in second part


def test_content_item_creation(tmpdir):
    # Test creating a ContentItem object
    test_file = tmpdir.join("test_file.txt")
    test_file.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")
    file_path = str(test_file)

    # Create a ContentItem with a full file reference
    content_item = ContentItem(file_path, file_path, [LineRange(1, "X")])
    assert content_item.original_arg == file_path
    assert content_item.file_path == file_path
    assert len(content_item.ranges) == 1
    assert content_item.ranges[0].start == 1
    assert content_item.ranges[0].end == "X"

    # Create a ContentItem with a specific line range
    content_item = ContentItem(f"{file_path}:L2-4", file_path, [LineRange(2, 4)])
    assert content_item.original_arg == f"{file_path}:L2-4"
    assert content_item.file_path == file_path
    assert len(content_item.ranges) == 1
    assert content_item.ranges[0].start == 2
    assert content_item.ranges[0].end == 4


def test_content_item_validate(tmpdir):
    # Test validating a ContentItem
    test_file = tmpdir.join("test_file.txt")
    test_file.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")
    file_path = str(test_file)

    # Valid ContentItem
    content_item = ContentItem(file_path, file_path, [LineRange(1, 5)])
    assert content_item.validate() is True

    # Invalid line range (out of bounds)
    content_item = ContentItem(file_path, file_path, [LineRange(1, 10)])
    with pytest.raises(ValueError):
        content_item.validate()

    # Invalid file path
    content_item = ContentItem("nonexistent.txt", "nonexistent.txt", [LineRange(1, 5)])
    with pytest.raises(FileNotFoundError):
        content_item.validate()


def test_content_item_get_content(tmpdir):
    # Test getting content from a ContentItem
    test_file = tmpdir.join("test_file.txt")
    test_file.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")
    file_path = str(test_file)

    # Full file
    content_item = ContentItem(file_path, file_path, [LineRange(1, "X")])
    assert content_item.get_content() == "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"

    # Single line
    content_item = ContentItem(file_path, file_path, [LineRange(3, 3)])
    assert content_item.get_content() == "Line 3"

    # Range
    content_item = ContentItem(file_path, file_path, [LineRange(2, 4)])
    assert content_item.get_content() == "Line 2\nLine 3\nLine 4"

    # Multiple ranges
    content_item = ContentItem(file_path, file_path, [LineRange(1, 1), LineRange(3, 4)])
    assert content_item.get_content() == "Line 1\nLine 3\nLine 4"


def test_create_content_item(tmpdir):
    # Test creating a ContentItem from a file path
    test_file = tmpdir.join("test_file.txt")
    test_file.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")
    file_path = str(test_file)

    # Full file
    content_item = create_content_item(file_path)
    assert content_item.file_path == file_path
    assert len(content_item.ranges) == 1
    assert content_item.ranges[0].is_full_file() is True

    # Single line
    content_item = create_content_item(f"{file_path}:L3")
    assert content_item.file_path == file_path
    assert len(content_item.ranges) == 1
    assert content_item.ranges[0].start == 3
    assert content_item.ranges[0].end == 3

    # Range
    content_item = create_content_item(f"{file_path}:L2-4")
    assert content_item.file_path == file_path
    assert len(content_item.ranges) == 1
    assert content_item.ranges[0].start == 2
    assert content_item.ranges[0].end == 4

    # Multiple ranges
    content_item = create_content_item(f"{file_path}:L1,L3-4")
    assert content_item.file_path == file_path
    assert len(content_item.ranges) == 2
    assert content_item.ranges[0].start == 1
    assert content_item.ranges[0].end == 1
    assert content_item.ranges[1].start == 3
    assert content_item.ranges[1].end == 4


def test_verify_content(tmpdir):
    # Test verifying a ContentItem
    test_file = tmpdir.join("test_file.txt")
    test_file.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")
    file_path = str(test_file)

    # Valid ContentItem
    content_item = create_content_item(file_path)
    verified_item = verify_content(content_item)
    assert verified_item is content_item

    # Invalid ContentItem (out of bounds)
    content_item = ContentItem(file_path, file_path, [LineRange(1, 10)])
    with pytest.raises(ValueError):
        verify_content(content_item)


def test_get_files_from_args(tmpdir):
    # Test getting ContentItems from arguments
    test_file1 = tmpdir.join("test_file1.txt")
    test_file1.write("Line 1\nLine 2\nLine 3")
    file_path1 = str(test_file1)

    test_file2 = tmpdir.join("test_file2.txt")
    test_file2.write("Line A\nLine B\nLine C")
    file_path2 = str(test_file2)

    # Single file
    content_items = get_files_from_args([file_path1])
    assert len(content_items) == 1
    assert content_items[0].file_path == file_path1

    # Multiple files
    content_items = get_files_from_args([file_path1, file_path2])
    assert len(content_items) == 2
    assert content_items[0].file_path == file_path1
    assert content_items[1].file_path == file_path2

    # File with line reference
    content_items = get_files_from_args([f"{file_path1}:L2"])
    assert len(content_items) == 1
    assert content_items[0].file_path == file_path1
    assert content_items[0].ranges[0].start == 2
    assert content_items[0].ranges[0].end == 2
