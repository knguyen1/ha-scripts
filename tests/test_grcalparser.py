from datetime import date

from utils.grcalparser import GlenRockNjCalendarParser

class TestGrCalParser:

    def test_basic_get(self):
        client = GlenRockNjCalendarParser(date(2023, 1, 1), date(2023, 1, 31), area_filter=["south/east", "boroughwide"])
        result = client.get_todays_items()

        assert False
