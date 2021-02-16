# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""CORS pre-flight decorator.

A simple decorator to add the options method to a Request Class.
"""
import calendar
from datetime import datetime, timedelta
from typing import Dict
from urllib.parse import parse_qsl

import pytz
from dpath import util as dpath_util
from flask import current_app

from .enums import CorpType

def get_nearest_business_day(val: datetime, include_today: bool = True) -> datetime:
    """Return fiscal year for the date."""
    if not include_today:
        val = get_next_day(val)
    if not is_holiday(val):
        return val
    else:
        return get_nearest_business_day(get_next_day(val))


def is_holiday(val: datetime) -> bool:
    """Return receipt number for payments."""
    """
        saturday or sunday check
        check the BC holidays
    """
    week_number: int = val.weekday()
    if week_number > 4:  # 5- saturday 6 sunday
        return True
    holidays_list = current_app.config.get('HOLIDAYS_IN_DATE_FORMAT')
    if val.date() in holidays_list:
        return True
    return False


def get_next_day(val: datetime):
    """Return previous day."""
    # index: 0 (current week), 1 (last week) and so on
    return val + timedelta(days=1)
