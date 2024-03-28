"""
Iterates over historical Germany wind forecast data and prints it to the screen.

Example run:
PYTHONPATH=py python examples/iterate_hist_forecast.py "localhost:50051"

License: MIT
Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""

import asyncio
import datetime
import sys

import grpc.aio as grpcaio
from frequenz.client.weather._client import Client
from frequenz.client.weather._types import ForecastFeature, Location

_service_address = sys.argv[1]


async def main(service_address: str) -> None:
    """Iterate over historical Germany wind forecast data and prints it to the screen.

    Args:
        service_address: The address of the service to connect to
            given in a form of a host followed by a colon and a port.
    """
    client = Client(
        grpcaio.insecure_channel(service_address),  # or secure channel with credentials
        service_address,
    )

    features = [
        ForecastFeature.V_WIND_COMPONENT_100_METRE,
        ForecastFeature.U_WIND_COMPONENT_100_METRE,
    ]

    locations = [
        Location(
            latitude=52.5,
            longitude=13.4,
            country_code="DE",
        ),
    ]

    now = datetime.datetime.utcnow()
    start = now - datetime.timedelta(days=1000)
    end = now + datetime.timedelta(days=0)

    location_forecast_iterator = client.hist_forecast_iterator(
        features=features, locations=locations, start=start, end=end
    )

    async for location_forecast in location_forecast_iterator:
        print(location_forecast.to_ndarray_vlf())
        #for forecasts in location_forecast.forecasts:
        #    print("Timestamp:", forecasts.valid_at_ts)
        #    for feature_forecast in forecasts.features:
        #        print(feature_forecast)


asyncio.run(main(_service_address))
