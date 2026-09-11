import unittest
from powerprotocol.rules import DomainRules
class DomainRuleTests(unittest.TestCase):
    def test_checksum(self): self.assertEqual(DomainRules.frame_checksum(bytes([1,2,3])),6)
    def test_map_requires_address(self):
        with self.assertRaises(ValueError): DomainRules.validate_point_map({"p":{}})
