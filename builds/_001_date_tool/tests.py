import unittest
from builds._001_date_tool.implementation import fetch_current_datetime
from datetime import datetime


class TestDateTool(unittest.TestCase):
    def test_fetch_current_datetime_format(self):
        """Test that the datetime format is correct."""
        current_datetime = fetch_current_datetime()
        # Example format: "2026-03-26 19:21:00"
        datetime_format = "%Y-%m-%d %H:%M:%S"

        try:
            datetime.strptime(current_datetime, datetime_format)
            valid_format = True
        except ValueError:
            valid_format = False
        
        self.assertTrue(valid_format, f"Datetime format is not valid: {current_datetime}")


if __name__ == '__main__':
    unittest.main()