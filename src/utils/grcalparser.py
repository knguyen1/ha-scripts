from collections import OrderedDict, defaultdict
from datetime import date, timedelta
from typing import Callable, DefaultDict, Dict, List, Optional

import requests
from dateutil import parser


class GlenRockNjCalendarParser:
    _parse_float: Optional[Callable] = None
    _object_pairs_hook = OrderedDict

    def __init__(
        self,
        session: Optional[requests.Session] = None,
        item_title_filter: Optional[List[str]] = None,
    ) -> None:
        self.item_title_filter = item_title_filter

        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        self.query_params = dict(option="com_dpcalendar", view="events", format="raw")

        self.session: requests.Session = session or requests.Session()
        self.base_api = "https://glenrocknj.net/index.php"

    def get_items(
        self, start_date: date, end_date: date, item_id: int, limit: int
    ) -> OrderedDict:
        query_params: Dict[str, str] = self.query_params.copy()
        query_params["limit"] = str(limit)
        query_params["ItemId"] = str(item_id)
        query_params["date-start"] = start_date.strftime("%Y-%m-%dT%H:%M:%S")
        query_params["date-end"] = end_date.strftime("%Y-%m-%dT%H:%M:%S")

        result = self._call_api("GET", self.base_api, params=query_params)
        result_json = self._parse_result_to_json(result)
        return result_json

    def get_todays_items(self, item_id: int = 965, limit: int = 0) -> List[str]:
        return self._get_the_days_items(date.today(), item_id, limit)

    def get_tomorrows_items(self, item_id: int = 965, limit: int = 0) -> List[str]:
        return self._get_the_days_items(
            date.today() + timedelta(days=1), item_id, limit
        )

    def get_the_years_items(
        self, item_id: int = 965, limit: int = 0
    ) -> DefaultDict[date, List[str]]:
        today = date.today()
        start_of_year = date(today.year, 1, 1)
        end_of_year = date(today.year, 12, 31)
        items = self._get_items_with_dates(start_of_year, end_of_year, item_id, limit)

        return items

    def _get_the_days_items(self, anchor: date, item_id: int, limit: int) -> List[str]:
        start_of_month = date.today().replace(day=1)
        next_month = date.today().replace(day=28) + timedelta(days=4)
        end_of_month = next_month - timedelta(days=next_month.day)
        items = self.get_items(start_of_month, end_of_month, item_id, limit)["data"]
        item_list = [
            item["title"]
            for item in items
            if parser.parse(item["start"]).date() == anchor
        ]
        return self._maybe_do_area_filter(item_list)

    def _get_items_with_dates(
        self, start_date: date, end_date: date, item_id: int, limit: int
    ) -> DefaultDict[date, List[str]]:
        items = self.get_items(start_date, end_date, item_id, limit)
        items = items["data"]

        result = defaultdict(list)
        for item in items:
            item_date = parser.parse(item["start"]).date()
            item_title = self._maybe_do_area_filter_str(item["title"])
            if item_title:
                result[item_date].append(item_title)

        return result

    def _maybe_do_area_filter(self, items: List[str]) -> List[str]:
        if not self.item_title_filter:
            return items

        return [
            item
            for item in items
            if any(match in item.lower() for match in self.item_title_filter)
        ]

    def _maybe_do_area_filter_str(self, item: str) -> Optional[str]:
        if not self.item_title_filter:
            return item

        if any(match in item.lower() for match in self.item_title_filter):
            return item
        else:
            return None

    def _parse_result_to_json(self, result: requests.Response):
        """
        Parse json from a response object
        """
        return result.json(
            object_pairs_hook=self._object_pairs_hook, parse_float=self._parse_float
        )

    def _call_api(self, method: str, url: str, **kwargs):
        """
        It calls the API with the given method.
        """
        headers = self.headers.copy()
        additional_headers = kwargs.pop("headers", {})
        headers.update(additional_headers)

        result = self.session.request(method, url, headers=headers, **kwargs)

        return result
