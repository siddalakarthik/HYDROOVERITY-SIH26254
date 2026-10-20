"""Reject corrupt/extra/path-traversal package payloads without extracting them."""
import hashlib
import importlib.util
import io
from pathlib import Path
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('m08_package', ROOT / 'hardware/package_m08.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PackageChecks(unittest.TestCase):
    def archive(self, data=b'reviewed digital figure', extra=False, name='figure.svg'):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as archive:
            archive.writestr(name, data)
            archive.writestr('SHA256SUMS.txt', hashlib.sha256(b'reviewed digital figure').hexdigest() + '  ' + name + '\n')
            if extra:
                archive.writestr('.env', 'UNREVIEWED_FILE')
        buffer.seek(0)
        return zipfile.ZipFile(buffer)

    def test_valid_checksum(self):
        with self.archive() as archive:
            module.verify_checksums(archive)

    def test_tampering_rejected(self):
        with self.archive(data=b'changed') as archive:
            with self.assertRaisesRegex(ValueError, 'Checksum mismatch'):
                module.verify_checksums(archive)

    def test_unlisted_file_rejected(self):
        with self.archive(extra=True) as archive:
            with self.assertRaisesRegex(ValueError, 'coverage differs'):
                module.verify_checksums(archive)

    def test_traversal_rejected(self):
        with self.archive(name='../personal.txt') as archive:
            with self.assertRaisesRegex(ValueError, 'Unsafe archive path'):
                module.verify_checksums(archive)


if __name__ == '__main__':
    unittest.main()
