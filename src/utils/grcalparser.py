from collections import OrderedDict
from datetime import date, timedelta
from typing import Callable, Dict, List, Optional

import requests
from dateutil import parser


class GlenRockNjCalendarParser:
    _parse_float: Optional[Callable] = None
    _object_pairs_hook = OrderedDict

    def __init__(
        self,
        start_date: date,
        end_date: date,
        item_id: int = 965,
        limit: int = 0,
        session: Optional[requests.Session] = None,
        area_filter: Optional[List[str]] = None,
    ) -> None:
        self.start_date = start_date
        self.end_date = end_date
        self.item_id = item_id
        self.limit = limit

        self.area_filter = area_filter

        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        self.session: requests.Session = session or requests.Session()
        self.base_api = "https://glenrocknj.net/index.php"

    def get_items(self) -> OrderedDict:
        query_params: Dict[str, str] = {}
        query_params["option"] = "com_dpcalendar"
        query_params["view"] = "events"
        query_params["format"] = "raw"
        query_params["limit"] = str(self.limit)
        query_params["ItemId"] = str(self.item_id)
        query_params["date-start"] = self.start_date.strftime("%Y-%m-%dT%H:%M:%S")
        query_params["date-end"] = self.end_date.strftime("%Y-%m-%dT%H:%M:%S")

        result = self._call_api("GET", self.base_api, params=query_params)
        result_json = self._parse_result_to_json(result)
        return result_json

    def get_todays_items(self) -> List[str]:
        return self._get_the_days_items(date.today())

    def get_tomorrows_items(self) -> List[str]:
        return self._get_the_days_items(date.today() + timedelta(days=1))

    def _get_the_days_items(self, anchor: date) -> List[str]:
        items = self.get_items()["data"]
        item_list = [
            item["title"]
            for item in items
            if parser.parse(item["start"]).date() == anchor
        ]
        return self._maybe_do_area_filter(item_list)

    def _maybe_do_area_filter(self, items: List[str]) -> List[str]:
        if not self.area_filter:
            return items

        return [
            item
            for item in items
            if any(match in item.lower() for match in self.area_filter)
        ]

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
