from datetime import date

from utils.grcalparser import GlenRockNjCalendarParser

class TestGrCalParser:

    def test_basic_get(self):
        client = GlenRockNjCalendarParser(date(2023, 1, 1), date(2023, 1, 31))
        result = client.get_items()

        assert False
