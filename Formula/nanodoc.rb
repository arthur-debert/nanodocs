class Nanodoc < Formula
  desc "A minimalist document bundler designed for stitching hints, reminders and short docs."
  homepage "https://github.com/arthur-debert/nanodoc/"
  url "https://files.pythonhosted.org/packages/source/n/nanodoc/nanodoc-0.1.1.tar.gz"
  sha256 "439e84b4a183b26c1514e352cdabdb850fee02e5ed17f59ecf3395cab23f787c"
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
