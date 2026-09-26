"""Tests for entropy_scanner.py"""

import pytest
from kevgate.entropy_scanner import shannon_entropy, scan_diff, has_critical_secret


class TestShannonEntropy:
    def test_empty_string_returns_zero(self):
        assert shannon_entropy("") == 0.0

    def test_single_char_returns_zero(self):
        assert shannon_entropy("a") == 0.0

    def test_two_identical_chars_low_entropy(self):
        assert shannon_entropy("aaaa") < 1.0

    def test_random_looking_string_high_entropy(self):
        # AWS key-like string should have high entropy
        assert shannon_entropy("AKIAIOSFODNN7EXAMPLE") > 3.5

    def test_english_prose_moderate_entropy(self):
        entropy = shannon_entropy("the quick brown fox jumps over the lazy dog")
        assert 3.5 < entropy < 5.0

    def test_base64_secret_high_entropy(self):
        # A realistic base64 secret
        secret = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        assert shannon_entropy(secret) > 4.0


class TestScanDiff:
    def test_clean_diff_no_findings(self):
        diff = """\
diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1,3 +1,3 @@
-# Old Title
+# New Title
 Some content here.
"""
        findings = scan_diff(diff)
        assert len(findings) == 0

    def test_aws_key_detected(self):
        diff = """\
diff --git a/config.py b/config.py
--- a/config.py
+++ b/config.py
@@ -1,2 +1,3 @@
+AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLEKEY"
 DEBUG = True
"""
        findings = scan_diff(diff)
        assert len(findings) >= 1
        assert any(f.pattern_name == "aws_access_key" for f in findings)

    def test_github_pat_detected(self):
        # Real GitHub PAT classic format: ghp_ followed by exactly 36 chars
        diff = """\
diff --git a/deploy.sh b/deploy.sh
--- a/deploy.sh
+++ b/deploy.sh
@@ -1,2 +1,3 @@
+GH_TOKEN=ghp_aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890
 echo "deploying"
"""
        findings = scan_diff(diff)
        assert any(f.pattern_name == "github_pat_classic" for f in findings)

    def test_private_key_header_detected(self):
        diff = """\
diff --git a/keys/id_rsa b/keys/id_rsa
--- /dev/null
+++ b/keys/id_rsa
@@ -0,0 +1,3 @@
+-----BEGIN RSA PRIVATE KEY-----
+MIIEpAIBAAKCAQEA...
+-----END RSA PRIVATE KEY-----
"""
        findings = scan_diff(diff)
        assert any(f.pattern_name == "private_key_header" for f in findings)

    def test_removed_lines_not_scanned(self):
        # Removed lines should not generate findings
        diff = """\
diff --git a/config.py b/config.py
--- a/config.py
+++ b/config.py
@@ -1,2 +1,2 @@
-AWS_KEY = "AKIAIOSFODNN7EXAMPLEKEY"
+AWS_KEY = os.environ["AWS_KEY"]
"""
        findings = scan_diff(diff)
        # The removed line should not be flagged
        assert not any(f.line_number == 5 for f in findings)  # line 5 is the '-' line

    def test_has_critical_secret_true(self):
        diff = '+SECRET_KEY = "AKIAIOSFODNN7EXAMPLEKEY"\n'
        findings = scan_diff(diff)
        assert has_critical_secret(findings)

    def test_has_critical_secret_false_on_empty(self):
        assert not has_critical_secret([])
