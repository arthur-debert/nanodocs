import pytest
import os
import subprocess
import tempfile
from nanodoc import create_header

# These are the sample files to test with
SAMPLE_FILES = [
    "/Users/adebert/h/nanodocpy/samples/cake.txt",
    "/Users/adebert/h/nanodocpy/samples/incident.txt", 
    "/Users/adebert/h/nanodocpy/samples/new-telephone.txt"
]

def test_e2e_with_nn_and_toc():
    """
    End-to-end test: process existing sample files with global line numbering and TOC.
    """
    # Verify sample files exist
    for file_path in SAMPLE_FILES:
        assert os.path.isfile(file_path), f"Sample file not found: {file_path}"
    
    # Run nanodoc with -nn and --toc options on the sample files
    result = subprocess.run(
        ["python", "nanodoc.py", "-nn", "--toc"] + SAMPLE_FILES,
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    
    # Calculate expected output parts (headers)
    toc_header = create_header("TOC")
    cake_header = create_header("cake.txt")
    incident_header = create_header("incident.txt")
    telephone_header = create_header("new-telephone.txt")
    
    # Count lines in sample files to build expectations
    with open(SAMPLE_FILES[0], 'r') as f:
        cake_lines = f.readlines()
    with open(SAMPLE_FILES[1], 'r') as f:
        incident_lines = f.readlines()
    with open(SAMPLE_FILES[2], 'r') as f:
        telephone_lines = f.readlines()
        
    # Extract just the important parts of the output for comparison (ignoring logs)
    output_lines = result.stdout.split("\n")
    start_index = next((i for i, line in enumerate(output_lines) if toc_header in line), 0)
    actual_output = "\n".join(output_lines[start_index:])
    
    # Basic assertions about content structure
    assert toc_header in actual_output, "TOC header not found in output"
    assert cake_header in actual_output, "cake.txt header not found"
    assert incident_header in actual_output, "incident.txt header not found"
    assert telephone_header in actual_output, "new-telephone.txt header not found"
    
    # Check for line numbering
    lines = actual_output.split('\n')
    for i, line in enumerate(lines):
        if any(str(n) + ": " in line for n in range(1, 100)):
            assert True  # Found line numbers
            break
    else:
        assert False, "No line numbers found in output"
    
    # Check TOC contains expected line numbers
    toc_section = actual_output.split(cake_header)[0]
    assert "cake.txt" in toc_section
    assert "incident.txt" in toc_section
    assert "new-telephone.txt" in toc_section
    
    # Line count sanity check
    numbered_lines = [line for line in lines if any(str(n) + ": " in line for n in range(1, 100))]
    assert len(numbered_lines) == len(cake_lines) + len(incident_lines) + len(telephone_lines)
    
def test_e2e_bundle_with_nn_and_toc(tmpdir):
    """
    End-to-end test: process existing sample files via a bundle file with global line numbering and TOC.
    """
    # Create bundle file referencing the sample files
    bundle_file = tmpdir.join("bundle.txt")
    bundle_file.write("\n".join(SAMPLE_FILES))
    
    # Run nanodoc with bundle file, -nn and --toc options
    result = subprocess.run(
        ["python", "nanodoc.py", "-nn", "--toc", str(bundle_file)],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    
    # Calculate expected output parts
    toc_header = create_header("TOC")
    cake_header = create_header("cake.txt")
    
    # Extract just the important parts of the output
    output_lines = result.stdout.split("\n")
    start_index = next((i for i, line in enumerate(output_lines) if toc_header in line), 0)
    actual_output = "\n".join(output_lines[start_index:])
    
    # Basic assertions about content
    assert toc_header in actual_output
    assert cake_header in actual_output
    assert os.path.basename(SAMPLE_FILES[1]) in actual_output  # incident.txt basename in output
    assert os.path.basename(SAMPLE_FILES[2]) in actual_output  # new-telephone.txt basename in output
    
    # Check for line numbering
    lines = actual_output.split('\n')
    for i, line in enumerate(lines):
        if any(str(n) + ": " in line for n in range(1, 100)):
            assert True  # Found line numbers
            break
    else:
        assert False, "No line numbers found in output"
    
    # Check TOC format has filenames and line numbers
    toc_section = actual_output.split(cake_header)[0]
    for sample_file in SAMPLE_FILES:
        filename = os.path.basename(sample_file)
        assert filename in toc_section, f"{filename} not found in TOC"
        # Check for line number pattern (filename followed by dots and a number)
        assert any(f"{filename} " in line and "..." in line and any(c.isdigit() for c in line) 
                  for line in toc_section.split('\n')), f"TOC entry format incorrect for {filename}"

def test_e2e_with_file_numbering_and_toc():
    """
    End-to-end test: process files with file-specific line numbering and TOC.
    Match expected output format exactly.
    """
    # Verify sample files exist
    for file_path in SAMPLE_FILES:
        assert os.path.isfile(file_path), f"Sample file not found: {file_path}"
    
    # Run nanodoc with -n and --toc options (file-specific line numbering)
    result = subprocess.run(
        ["python", "nanodoc.py", "-n", "--toc", "samples"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    
    # Calculate expected output parts (headers)
    toc_header = create_header("TOC")
    cake_header = create_header("cake.txt")
    incident_header = create_header("incident.txt")
    telephone_header = create_header("new-telephone.txt")
    
    # Extract just the important parts of the output for comparison (ignoring logs)
    output_lines = result.stdout.split("\n")
    start_index = next((i for i, line in enumerate(output_lines) if toc_header in line), 0)
    actual_output = "\n".join(output_lines[start_index:])
    
    # Verify TOC format with specific line numbers
    toc_section = actual_output.split(cake_header)[0]
    assert "cake.txt" in toc_section
    assert "incident.txt" in toc_section
    assert "new-telephone.txt" in toc_section
    
    # Check for specific line numbering patterns per file
    cake_section = actual_output.split(cake_header)[1].split(incident_header)[0]
    incident_section = actual_output.split(incident_header)[1].split(telephone_header)[0]
    telephone_section = actual_output.split(telephone_header)[1]
    
    # Verify file-specific numbering (starts from 1 for each file)
    assert "   1: " in cake_section
    assert "   1: " in incident_section
    assert "   1: " in telephone_section
    
    # Check each section has its own line numbers (not continuing from previous file)
    assert "   5: Michael Scott, Regional Manager" in cake_section
    assert "   9: Michael Scott, Regional Manager." in incident_section
    assert "  10: Corporate (via Michael Scott)" in telephone_section
    
    # Verify TOC has expected line numbers - they match the example output
    assert any("cake.txt" in line and "7" in line for line in toc_section.split("\n"))
    assert any("incident.txt" in line and "13" in line for line in toc_section.split("\n"))
    assert any("new-telephone.txt" in line and "23" in line for line in toc_section.split("\n"))
