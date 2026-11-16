import unittest

from bounty_dex import build_virtual_app_args, parse_adb_devices


class DeviceParsingTests(unittest.TestCase):
    def test_only_authorized_devices_are_returned(self):
        output = """List of devices attached
R58M123456A device product:a16 model:SM_A165F
192.168.1.25:37123 device
R58M000000 unauthorized
emulator-5554 offline
"""
        self.assertEqual(
            parse_adb_devices(output),
            ["R58M123456A", "192.168.1.25:37123"],
        )


class VirtualWindowArgumentTests(unittest.TestCase):
    def test_builds_separate_landscape_virtual_display(self):
        args = build_virtual_app_args(
            "R58M123456A", "com.android.settings", 1280, 30
        )
        self.assertIn("--new-display=1280x800/160", args)
        self.assertIn("--flex-display", args)
        self.assertIn("--start-app=com.android.settings", args)
        self.assertIn("--mouse=uhid", args)
        self.assertIn("--keyboard=sdk", args)
        self.assertIn("--max-fps=30", args)
        self.assertEqual(args[:2], ["-s", "R58M123456A"])

    def test_supports_wifi_serial(self):
        args = build_virtual_app_args(
            "192.168.1.25:5555", "com.google.android.youtube", 720, 60
        )
        self.assertEqual(args[:2], ["-s", "192.168.1.25:5555"])
        self.assertIn("--new-display=720x450/160", args)

    def test_rejects_invalid_package(self):
        with self.assertRaises(ValueError):
            build_virtual_app_args("device", "com.example;bad", 1280, 30)

    def test_rejects_unsupported_resolution_and_fps(self):
        with self.assertRaises(ValueError):
            build_virtual_app_args("device", "com.example.app", 999, 30)
        with self.assertRaises(ValueError):
            build_virtual_app_args("device", "com.example.app", 1280, 24)


if __name__ == "__main__":
    unittest.main()
