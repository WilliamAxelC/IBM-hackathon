"""Tests for diff_parser.py"""

import pytest
from kevgate.diff_parser import parse_unified_diff, filter_triageable, DiffChunk


SAMPLE_DIFF = """\
diff --git a/src/auth.py b/src/auth.py
index 1234567..abcdefg 100644
--- a/src/auth.py
+++ b/src/auth.py
@@ -10,6 +10,7 @@ class AuthService:
     def login(self, username: str, password: str):
         query = "SELECT * FROM users WHERE name = '%s'" % username
+        query = f"SELECT * FROM users WHERE name = '{username}'"
         return self.db.execute(query)
 
 class UserController:
diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1,3 +1,3 @@
-# Old Title
+# New Title
"""

LOCKFILE_DIFF = """\
diff --git a/package-lock.json b/package-lock.json
--- a/package-lock.json
+++ b/package-lock.json
@@ -1,5 +1,5 @@
-  "version": "1.0.0",
+  "version": "1.0.1",
"""

NEW_FILE_DIFF = """\
diff --git a/src/new_module.py b/src/new_module.py
new file mode 100644
--- /dev/null
+++ b/src/new_module.py
@@ -0,0 +1,3 @@
+def hello():
+    return "world"
"""


class TestParseUnifiedDiff:
    def test_parses_two_files(self):
        chunks = parse_unified_diff(SAMPLE_DIFF)
        assert len(chunks) == 2

    def test_first_file_path(self):
        chunks = parse_unified_diff(SAMPLE_DIFF)
        assert chunks[0].file_path == "src/auth.py"

    def test_second_file_path(self):
        chunks = parse_unified_diff(SAMPLE_DIFF)
        assert chunks[1].file_path == "README.md"

    def test_added_lines_captured(self):
        chunks = parse_unified_diff(SAMPLE_DIFF)
        auth_chunk = chunks[0]
        assert any("username" in line for line in auth_chunk.added_lines)

    def test_removed_lines_captured(self):
        chunks = parse_unified_diff(SAMPLE_DIFF)
        readme_chunk = chunks[1]
        assert any("Old Title" in line for line in readme_chunk.removed_lines)

    def test_new_file_flag(self):
        chunks = parse_unified_diff(NEW_FILE_DIFF)
        assert len(chunks) == 1
        assert chunks[0].is_new_file is True

    def test_empty_diff_returns_empty_list(self):
        assert parse_unified_diff("") == []


class TestLockfileDetection:
    def test_package_lock_is_lockfile(self):
        chunks = parse_unified_diff(LOCKFILE_DIFF)
        assert len(chunks) == 1
        assert chunks[0].is_lockfile is True

    def test_auth_py_is_not_lockfile(self):
        chunks = parse_unified_diff(SAMPLE_DIFF)
        assert chunks[0].is_lockfile is False

    def test_lockfile_filtered_out(self):
        chunks = parse_unified_diff(LOCKFILE_DIFF)
        triageable = filter_triageable(chunks)
        assert len(triageable) == 0

    def test_normal_files_not_filtered(self):
        chunks = parse_unified_diff(SAMPLE_DIFF)
        triageable = filter_triageable(chunks)
        assert len(triageable) == 2
