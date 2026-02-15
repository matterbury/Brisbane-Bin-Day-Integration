# Brisbane Bin Day Sensor

This project creates a Home Assistant device with a number of sensors
that provide details of bin collections in the Brisbane City Council
area.  The 'main' sensor `Is Bin Time` indicates whether it's time to
take the bins out, while two more indicate which bins: one for the
"normal" (green waste bin) week, another for the recycling (yellow
bin) week. Note that the red general rubbish bin is [assumed to be]
collected every week. These sensors can be used to create
alerts/automations in Home Assistant with names specific to the bins
being collected.

While most Councils provide details of their waste collection
schedules via their Open Data portals there is no consistency or
standards in how the data is structured (especially when it comes to
the recycling week determination).  Therefore, it is not possible to
create a generic sensor but you are welcome to fork this code and
cusrtomize it for your particular Council.

## Installation (HACS) - Recommended
0. Install [HACS](https://custom-components.github.io/hacs/installation/manual/), this will allow you to easily update
1. Add `https://github.com/matterbury/Brisbane-Bin-Day` as a [custom repository](https://custom-components.github.io/hacs/usage/settings/#add-custom-repositories) as Type: Integration
2. Restart your instance.

## Installation (Manual)
1. Download this repository as a ZIP (green button, top right) and unzip the archive
2. Copy `/custom_components/bin_day` to your `<config_dir>/custom_components/` directory
   * You will need to create the `custom_components` folder if it does not exist
   * On Hassio the final location will be `/config/custom_components/bin_day`
   * On Hassbian the final location will be `/home/homeassistant/.homeassistant/custom_components/bin_day`

## Configuration

You will need to obtain your property number from the
[Brisbane City Council Waste Collection Open Data Site](https://data.brisbane.qld.gov.au/explore/dataset/waste-collection-days-collection-days/table/).
Search for your address and copy the value in the Property_Number column of the table.

Configuration is via the UI: Settings > Devices & services > blue "+ Add integration" button at the bottom right.
Search for "bin day" and click it, which will take you to the configuration form:

- **Name of the service in Home Assistant**: self evident
- **The URL to the BCC API, including '{dataset}' and '{query}' parameters**: advanced users only
- **Name of the collection days dataset**: advanced users only
- **Name of the collection weeks dataset**: advanced users only
- **How frequently (in hours) to poll the BCC API**: minimum is 6 hours to avoid spamming the server, 24 hours is fine for most uses
- **The mdi:icon to use for the normal/green waste week entity**: self evident
- **The mdi:icon to use for the recycling week entity**: self evident
- **Hours in advance of midnight on collection day to alert**: see below
- **The id number of the collection property**: **REQUIRED** see above
- **True if you have a green bin for collection, else False**: self evident
     
The `Is Bin Time` sensor is `False` until the current time is within
the window set by *Hours in advance ...* before midnight at the start
of collection day.

For example, if your collection day is Wednesday, the *Next Collection
Date* will be `00:00:00` on the next Wednesday (the **start** of the
day), and if *Alert Hours* is 12 hours, `Is Bin Time` will become
`True` at midday the immediately preceding Tuesday (and become `False`
again at midnight Wednesday).

## Sensors

The integration creates a number of sensors. Note that all `id`'s are
prefixed with `bin_day_` to avoid namespace collisions.

Those grouped under `Diagnostic` are configuration items or pulled
from the council API (such as your collection and address details) and
are [mostly] static.

Those grouped under `Sensors` are computed dynamically:

- **Due In Hours**: How many whole hours until the *Next Collection Date* (the ceiling, so `5.23` becomes `6` f.ex)
- **Extra Bin Text**: Text explaining what other bin needs to be put out, if any, else blank
- **Is Bin Time**: True iff we are in the `Alert Hours` window before collection day.
- **Is Green Waste Week**: True iff the next collection includes the green bin.
- **Is Recycling Week**: True iff the next collection includes the recycling bin.
- **Next Collection Date**: Midnight at the start of the next collection day.

Both `Is Green Waste Week` and `Is Recycling Week` can be `False` (and
`Extra Bin Text` empty) if you don't have a green bin, otherwise one
or the other will always be `True`.

## Alerts

Home assistant alerts that use notifications can be setup to monitor
the state of the sensors, although, given how limited they are,
automations are much more useful.  Here are some examples.

```yaml
alert:
  take_the_bins_out:
    name: Take the bins out
    entity_id: sensor.bin_day_is_bin_time
    state: "True"
    repeat: 1
    can_acknowledge: false
    skip_first: false
    message: "Take the bins out!"
    notifiers:
      - persistent_notification
```

```yaml
automation:
  - alias: Take out the red and yellow bins
    triggers:
      - trigger: state
        entity_id: sensor.bin_day_is_bin_time
        to: "on"
    conditions:
      - condition: state
        entity_id: sensor.bin_day_is_recycling_week
        state: "on"
    actions:
      - action: notify.persistent_notification
        data:
          message: "Take out the red and yellow bins!"
```
## Reporting an Issue

1. Enable debug logging for this component using the three dots menu at the top right of the integration page.
2. Verify you're still having the issue
3. Extract your logs: Settings > System > Logs; you might need to switch to raw logs using the three dots menu
3. File an issue in this integration's Github Repository. Include your log data:
   (Developer section > Info > Load Full Home Assistant Log)
   * You can paste your log file at pastebin https://pastebin.com/ and submit a link.
   * Please include details about your setup (Pi, NUC, etc, docker?, HASSOS?)
   * The log file can also be found at `/<config_dir>/home-assistant.log`
