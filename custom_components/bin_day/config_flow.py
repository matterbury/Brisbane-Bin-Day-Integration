"""Config flow for Brisbane Bin Day."""

from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow
)
from homeassistant.const import CONF_NAME
from homeassistant.core import callback

from .const import (
    DOMAIN,
    CONF_SENSOR_NAME,
    CONF_PROPERTY_NUMBER,
    CONF_BASE_URL,
    CONF_DAYS_TABLE,
    CONF_WEEKS_TABLE,
    CONF_POLLING_INTERVAL_HOURS,
    CONF_NORMAL_ICON,
    CONF_RECYCLING_ICON,
    CONF_ALERT_HOURS,
    CONF_HAS_GREEN_BIN,
    DEFAULT_SENSOR_NAME,
    DEFAULT_BASE_URL,
    DEFAULT_DAYS_TABLE,
    DEFAULT_WEEKS_TABLE,
    DEFAULT_POLLING_INTERVAL_HOURS,
    DEFAULT_ICON,
    DEFAULT_ALERT_HOURS,
    MINIMUM_POLLING_INTERVAL_HOURS,
)


class BinDayFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Brisbane Bin Day."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> BinDayOptionFlowHandler:
        """Get the options flow for this handler."""
        return BinDayOptionFlowHandler()

    def is_matching(self, other_flow: ConfigFlow) -> bool:
        """Return True if other_flow matches this flow."""
        return other_flow.context.get("unique_id") == self.context.get("unique_id")

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle a flow initiated by the user."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data={},
                options={
                    CONF_SENSOR_NAME: user_input[CONF_SENSOR_NAME],
                    CONF_PROPERTY_NUMBER: user_input[CONF_PROPERTY_NUMBER],
                    CONF_BASE_URL: user_input[CONF_BASE_URL],
                    CONF_DAYS_TABLE: user_input[CONF_DAYS_TABLE],
                    CONF_WEEKS_TABLE: user_input[CONF_WEEKS_TABLE],
                    CONF_POLLING_INTERVAL_HOURS: user_input[CONF_POLLING_INTERVAL_HOURS],
                    CONF_NORMAL_ICON: user_input[CONF_NORMAL_ICON],
                    CONF_RECYCLING_ICON: user_input[CONF_RECYCLING_ICON],
                    CONF_ALERT_HOURS: user_input[CONF_ALERT_HOURS],
                    CONF_HAS_GREEN_BIN: user_input[CONF_HAS_GREEN_BIN],
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PROPERTY_NUMBER): int,
                }
            ),
        )


class BinDayOptionFlowHandler(OptionsFlow):
    """Handle options."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_PROPERTY_NUMBER,
                        default=self.config_entry.options[CONF_PROPERTY_NUMBER]
                    ): int,
                }
            ),
            errors={},
        )
