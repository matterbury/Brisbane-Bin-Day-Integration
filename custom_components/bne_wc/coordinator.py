"""Coordinator for the polling of the BCC API."""

import logging

from datetime import timedelta
from urllib.parse import quote_plus

import async_timeout
import pandas
import requests

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN,
    CONF_POLLING_INTERVAL_HOURS,
    CONF_BASE_URL,
    CONF_WASTE_DAYS_TABLE,
    CONF_WASTE_WEEKS_TABLE,
    CONF_PROPERTY_NUMBER,
)

from .collection_data import BccApiData

_LOGGER = logging.getLogger(__name__)


class BccApiDataUpdateCoordinator(DataUpdateCoordinator[BccApiData]):
    """Coordinates requests to the BCC API."""

    _config: ConfigEntry

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the BCC API coordinator."""
        self._config = config_entry

        polling_interval = config_entry.options.get(CONF_POLLING_INTERVAL_HOURS)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=config_entry,
            update_interval=timedelta(hours=polling_interval),
            always_update=False
        )

    async def _async_update_data(self) -> BccApiData:
        """Fetch the data from the BCC API and parse it and return it."""
        property_number = self._config.options.get(CONF_PROPERTY_NUMBER)
        due_in_hours = self._config.options.get(CONF_DUE_IN_HOURS)
        green_bin = self._config.options.get(CONF_GREEN_BIN)
        api_data = BccApiData(property_number, due_in_hours, green_bin)

        base_url = self._config.options.get(CONF_BASE_URL)
        days_table = self._config.options.get(CONF_WASTE_DAYS_TABLE)
        weeks_table = self._config.options.get(CONF_WASTE_WEEKS_TABLE)
        self._get_days_data(base_url, days_table, property_number, api_data)
        self._get_weeks_data(base_url, weeks_table, api_data)

        return api_data

    def _get_days_data(self, base_url, days_table, property_number, api_data):
        """Fetch the data that the days table provides."""

        # Note: asyncio.TimeoutError and aiohttp.ClientError are already
        # handled by the data update coordinator.
        async with async_timeout.timeout(10):
            try:
                full_url = base_url.format(**{
                    'dataset': days_table,
                    'query': quote_plus(f"property_id={property_number}")
                })

                response = requests.get(full_url, timeout=60)
                json=response.json()

                if 'error_code' in json:
                    _LOGGER.error(
                        "Error retrieving collection day dataset: %s: %s",
                        json['error_code'], json['message'])
                else:
                    dic = json['results']
                    df = pandas.DataFrame(dic)

                    if len(df.index) > 0:
                        api_data.suburb = df['suburb'].iloc[0]
                        api_data.street = df['street_name'].iloc[0]
                        api_data.house_number = df['house_number'].iloc[0]
                        api_data.collection_day = df['collection_day'].iloc[0]
                        api_data.collection_zone = int(df['zone'].iloc[0])
                    else:
                        _LOGGER.error('Collection day dataset zero rows returned')

            except requests.exceptions.RequestException:
                _LOGGER.exception("Error requetsing collection day data")

    def _get_weeks_data(self, base_url, weeks_table, api_data):
        """Fetch the data that the weeks table provides.""" 

        week_start_date = (
            api_data.next_collection_date() -
            timedelta(days=api_data.collection_week_day())
        )
        query_date = f'{week_start_date:%Y-%m-%d}'.replace("'", "\\'")
        query_zone = str(api_data.collection_zone).replace("'", "\\'")
        query = f"week_starting=date'{query_date}' AND search(zone,'{query_zone}')"

        # Note: asyncio.TimeoutError and aiohttp.ClientError are already
        # handled by the data update coordinator.
        async with async_timeout.timeout(10):
            try:
                full_url = base_url.format(**{
                    'dataset': weeks_table,
                    'query': quote_plus(query)
                })

                response = requests.get(full_url, timeout=60)
                json=response.json()

                if 'error_code' in json:
                    _LOGGER.error(
                        "Error retrieving collection week dataset: %s: %s",
                        json['error_code'], json['message'])
                else:
                    dic = json['results']
                    df = pandas.DataFrame(dic)

                    api_data.recycling_week = len(df.index) > 0

            except requests.exceptions.RequestException:
                _LOGGER.exception("Error requesting collection week data")
