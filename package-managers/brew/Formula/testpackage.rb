class Testpackage < Formula
  desc "Test package."
  homepage "http://www.jarn.com/"
  url "https://files.pythonhosted.org/packages/source/t/testpackage/testpackage-2.27.tar.gz"
  sha256 "REPLACE_WITH_ACTUAL_SHA256"
  license "MIT"

  depends_on "python@3"

  def install
    # Install using pip
    system "pip3", "install", "--prefix=#{prefix}", "testpackage==#{version}"

    # Create wrapper script that uses python -m nanodoc
    (bin/"testpackage").write <<~EOS
      #!/bin/bash
      python3 -m testpackage "$@"
    EOS
    chmod 0755, bin/"testpackage"
  end

  test do
    # Test using the wrapper script
    system bin/"testpackage", "--help"

    # Also test using python -m directly
    system "python3", "-m", "testpackage", "--help"
  end
end