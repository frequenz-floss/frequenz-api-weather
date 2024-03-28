# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""The Historical Forecast Iterator."""

from datetime import datetime
from typing import Any, AsyncIterator, List

from frequenz.api.common.pagination import pagination_params_pb2
from frequenz.api.weather import weather_pb2, weather_pb2_grpc
from google.protobuf import timestamp_pb2

from ._types import ForecastFeature, Forecasts, Location

PAGE_SIZE = 20
EMPTY_PAGE_TOKEN = ""


class HistoricalForecastIterator(AsyncIterator[weather_pb2.LocationForecast]):
    """An iterator over historical weather forecasts."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        stub: weather_pb2_grpc.WeatherForecastServiceStub,
        locations: list[Location],
        features: list[ForecastFeature],
        start: datetime,
        end: datetime,
    ) -> None:
        """Initialize the iterator.

        Args:
            stub: The gRPC stub to use for communication with the API.
            locations: Locations to get historical weather forecasts for.
            features: Features to get historical weather forecasts for.
            start: Start of the time range to get historical weather forecasts for.
            end: End of the time range to get historical weather forecasts for.
        """
        self._stub = stub
        self.locations = locations
        self.features = features

        self.start_ts = timestamp_pb2.Timestamp()
        self.start_ts.FromDatetime(start)
        self.end_ts = timestamp_pb2.Timestamp()
        self.end_ts.FromDatetime(end)

        self.location_forecasts: List[weather_pb2.LocationForecast] = []
        self.page_token = None

    def __aiter__(self) -> "HistoricalForecastIterator":
        """Return the iterator.

        Returns:
            The iterator.
        """
        return self

    async def __anext__(self) -> weather_pb2.LocationForecast:
        """Get the next historical weather forecast.

        Returns:
            The next historical weather forecast.

        Raises:
            StopAsyncIteration: If there are no more historical weather forecasts.
        """
        if len(self.location_forecasts) == 0 and self.page_token == EMPTY_PAGE_TOKEN:
            raise StopAsyncIteration

        if self.location_forecasts is None or len(self.location_forecasts) == 0:
            pagination_params = pagination_params_pb2.PaginationParams()
            pagination_params.page_size = PAGE_SIZE
            if self.page_token is not None:
                pagination_params.page_token = self.page_token

            response: Any = (
                await self._stub.GetHistoricalWeatherForecast(  # type:ignore
                    weather_pb2.GetHistoricalWeatherForecastRequest(
                        locations=(location.to_pb() for location in self.locations),
                        features=(feature.value for feature in self.features),
                        start_ts=self.start_ts,
                        end_ts=self.end_ts,
                        pagination_params=pagination_params,
                    )
                )
            )

            self.page_token = response.pagination_info.next_page_token
            self.location_forecasts = response.location_forecasts

        location_forecast: weather_pb2.LocationForecast = self.location_forecasts.pop(0)
        return Forecasts.from_pb(location_forecast)
