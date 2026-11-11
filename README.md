# Geely Telemetry for Home Assistant

A custom Home Assistant integration and companion in-car app for Geely vehicle telemetry. The integration exposes a curated set of useful sensors and a GPS tracker. MQTT and webhook destinations from the app can carry the complete JSON telemetry frame.

## Features

- Vehicle speed, gear, traction battery, range, trip values, charging values, and connection status.
- A `device_tracker` GPS entity for the Home Assistant map card.
- Receive app data over HTTPS through Home Assistant OAuth, or read the vehicle over the local network.
- The app can continue to publish the full readable VHAL property set to MQTT or webhook destinations.

## Install with HACS

1. In HACS, open **Integrations** and choose **Custom repositories** from the menu.
2. Add `https://github.com/BRITONETO25/geely-telemetry-ha` with category **Integration**.
3. Download **Geely Telemetry** and restart Home Assistant.
4. Add the integration. Select **Car app over the internet** for remote push or **Local network** for LAN polling.
5. In the in-car app, select **Home Assistant**, enter your public `https://` Home Assistant URL, and tap **Authenticate**.
6. Approve access on the Home Assistant sign-in page and return to the in-car app.

For the map, add a **Map** dashboard card and select the integration's `device_tracker` entity.

## Privacy and requirements

The in-car app needs Android location permission to send GPS coordinates. Telemetry is sent only to the destinations enabled in the app. OAuth tokens are stored encrypted on the head unit. The app reads vehicle signals and location; it does not send vehicle control commands.

The integration currently exposes a small everyday sensor set. The odometer is not available in the current VHAL snapshot on the tested vehicle.

## Support

Report bugs and feature requests in the repository's GitHub Issues page.

## License

MIT license.
