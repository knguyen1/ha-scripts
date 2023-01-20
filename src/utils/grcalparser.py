from collections import OrderedDict
from datetime import date
from typing import Callable, Dict, Optional

import requests


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
    ) -> None:
        self.start_date = start_date
        self.end_date = end_date
        self.item_id = item_id
        self.limit = limit

        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        self.session: requests.Session = session or requests.Session()
        self.base_api = "https://glenrocknj.net/index.php"

    def get_items(self) -> Dict[str, object]:
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

        assert True

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
