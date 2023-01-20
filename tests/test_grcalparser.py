from datetime import date

from utils.grcalparser import GlenRockNjCalendarParser


class TestGrCalParser:
    def test_basic_get(self):
        client = GlenRockNjCalendarParser(
            item_title_filter=["south/east", "boroughwide"],
        )
        result = client.get_the_years_items()

        assert False
