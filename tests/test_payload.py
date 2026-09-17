import json
import re
import unittest


def encode_payload(device_id, uid, rhost, rport):
    return json.dumps(
        {"id": device_id, "uid": str(uid), "rhost": rhost, "rport": str(rport)},
        separators=(",", ":"),
    )


class PayloadTests(unittest.TestCase):
    def test_json_survives_quotes_in_id(self):
        raw = encode_payload('abc"def', 0, "127.0.0.1", 443)
        parsed = json.loads(raw)
        self.assertEqual(parsed["id"], 'abc"def')
        self.assertEqual(parsed["uid"], "0")
        self.assertEqual(parsed["rhost"], "127.0.0.1")
        self.assertEqual(parsed["rport"], "443")

    def test_status_regex_matches_php_json_encode(self):
        html = '<script>document.getElementById(\'bk\').value = 4132;</script>'
        match = re.search(
            r"document\.getElementById\('bk'\)\.value\s*=\s*'?(\d+)'?",
            html,
        )
        self.assertIsNotNone(match)
        self.assertEqual(int(match.group(1)), 4132)


if __name__ == "__main__":
    unittest.main()
