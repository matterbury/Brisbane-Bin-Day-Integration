"""Constants for Brisbane Bin Day."""

from __future__ import annotations
from typing import Final

DOMAIN: Final = 'bne_wc'

CONF_SENSOR_NAME: Final = 'sensor_name'
CONF_PROPERTY_NUMBER: Final = 'property_number'
CONF_BASE_URL: Final = 'base_url'
CONF_DAYS_TABLE: Final = 'days_table'
CONF_WEEKS_TABLE: Final = 'weeks_table'
CONF_POLLING_INTERVAL_HOURS: Final = 'polling_interval'
CONF_NORMAL_ICON: Final = 'icon'
CONF_RECYCLING_ICON: Final = 'recycling_icon'
CONF_ALERT_HOURS: Final = 'alert_hours'
CONF_HAS_GREEN_BIN: Final = 'has_green_bin'

DEFAULT_SENSOR_NAME: Final = 'Brisbane Bin Day'
DEFAULT_BASE_URL: Final = (
    'https://www.data.brisbane.qld.gov.au/api/explore/v2.1/catalog/datasets/'
    '{dataset}/records?where={query}&limit=1')
DEFAULT_DAYS_TABLE: Final = 'waste-collection-days-collection-days'
DEFAULT_WEEKS_TABLE: Final = 'waste-collection-days-collection-weeks'
DEFAULT_ALERT_HOURS: Final = 12
DEFAULT_POLLING_INTERVAL_HOURS: Final = 24
DEFAULT_ICON: Final = 'mdi:trash-can'

MINIMUM_POLLING_INTERVAL_HOURS: Final = 6
