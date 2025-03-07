import pytest
import os
from nanodoc import expand_bundles

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
    with pytest.raises(SystemExit) as excinfo:
        expand_bundles("non_existent_bundle.txt")
    assert excinfo.value.code == 127
