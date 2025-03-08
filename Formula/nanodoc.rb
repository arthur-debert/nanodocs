class Nanodoc < Formula
  desc "A minimalist document bundler designed for stitching hints, reminders and short docs."
  homepage "https://github.com/arthur-debert/nanodoc/"
  url "https://files.pythonhosted.org/packages/source/n/nanodoc/nanodoc-0.3.1.tar.gz"
  sha256 "5e76c12170dfdc4e3363cda0bdf32b104252ebec7c5a17fe8488f532304e6335"
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
