import pytest
import os
from nanodoc.nanodoc import expand_bundles
from nanodoc.nanodoc import BundleError

def test_expand_bundles_valid(tmpdir):
    bundle_file = tmpdir.join("test_bundle.txt")
    test_file1 = tmpdir.join("test_file1.txt")
    test_file1.write("Line 1")
    test_file2 = tmpdir.join("test_file2.txt")
    test_file2.write("Line 2")
    bundle_file.write(str(test_file1) + "\n" + str(test_file2))

    expanded_files = expand_bundles(str(bundle_file))
    assert str(test_file1) in expanded_files
    assert str(test_file2) in expanded_files

def test_expand_bundles_not_found(tmpdir):
    with pytest.raises(BundleError) as excinfo:
        expand_bundles("non_existent_bundle.txt")
    assert "Bundle file not found" in str(excinfo.value)

def test_expand_bundles_no_valid_files(tmpdir):
    bundle_file = tmpdir.join("test_bundle.txt")
    bundle_file.write("/nonexistent/file1.txt\n/nonexistent/file2.txt")

    with pytest.raises(BundleError) as excinfo:
        expand_bundles(str(bundle_file))
    assert "No valid files found in bundle" in str(excinfo.value)
