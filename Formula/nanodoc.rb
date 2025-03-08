  Downloading nanodoc-0.3.1-py3-none-any.whl.metadata (4.8 kB)
Downloading nanodoc-0.3.1-py3-none-any.whl (14 kB)
class Nanodoc < Formula
  desc "A minimalist document bundler designed for stitching hints, reminders and short docs."
  homepage "https://github.com/arthur-debert/nanodoc/"
  url "https://files.pythonhosted.org/packages/source/n/nanodoc/nanodoc-0.3.1.tar.gz"
  sha256 "5e76c12170dfdc4e3363cda0bdf32b104252ebec7c5a17fe8488f532304e6335"
  license "MIT"

  depends_on "python@3"
  depends_on "poetry"

  def install
    system "poetry", "install"

    # Create wrapper script for pmrun
    (bin/"pmrun").write <<~EOS
      #!/bin/bash
      cd #{prefix} && poetry run pmrun "$@"
    EOS
    chmod 0755, bin/"pmrun"
  end

  test do
    system "#{bin}/pmrun", "--help"
  end
end
