class Nanodoc < Formula
  desc "A minimalist document bundler designed for stitching hints, reminders and short docs."
  homepage "https://github.com/arthur-debert/nanodoc/"
  url "https://files.pythonhosted.org/packages/source/n/nanodoc/nanodoc-0.6.4.tar.gz"
  sha256 "8afbd0bf14cab9b81734affb360df028a638f4a529e1e4a61600450585c991c6"
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