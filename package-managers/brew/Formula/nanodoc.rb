class Nanodoc < Formula
  desc "A minimalist document bundler designed for stitching hints, reminders and short docs."
  homepage "https://github.com/arthur-debert/nanodoc/"
  url "https://files.pythonhosted.org/packages/source/n/nanodoc/nanodoc-0.6.2.tar.gz"
  sha256 "cf72b546980cd7dce1291aecd0f3ce400e4bc3b6b3cfc72e053563ad9f9b0674"
  license "MIT"

  depends_on "python@3"

  def install
    # Install using pip
    system "pip3", "install", "--prefix=#{prefix}", "nanodoc==#{version}"

    # Create wrapper script that uses python -m nanodoc
    (bin/"nanodoc").write <<~EOS
      #!/bin/bash
      python3 -m nanodoc "$@"
    EOS
    chmod 0755, bin/"nanodoc"
  end

  test do
    # Test using the wrapper script
    system bin/"nanodoc", "--help"

    # Also test using python -m directly
    system "python3", "-m", "nanodoc", "--help"
  end
end
