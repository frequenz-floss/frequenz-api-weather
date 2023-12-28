# License: MIT
# Copyright © 2023 Frequenz Energy-as-a-Service GmbH

"""Test the types module."""

# pylint doesn't understand fixtures. It thinks it is redefined name.
# pylint: disable=redefined-outer-name

# pylint doesn't understand the imports from the generated proto modules.
# pylint: disable=no-name-in-module,no-member

from datetime import timedelta

import numpy as np
from _pytest.logging import LogCaptureFixture
from frequenz.api.weather import weather_pb2
from frequenz.api.weather.location_pb2 import Location as LocationProto
from frequenz.client.weather._types import ForecastFeature, Forecasts, Location
from google.protobuf.timestamp_pb2 import Timestamp
from pytest import fixture


class TestForecastFeatureType:
    """Testing the ForecastFeature type."""

    def test_from_pb_valid(self) -> None:
        """Test if the method works correctly when a valid value is passed."""
        forecast_feature_pb_value = (
            weather_pb2.ForecastFeature.FORECAST_FEATURE_U_WIND_COMPONENT_100_METRE
        )
        result = ForecastFeature.from_pb(forecast_feature_pb_value)
        assert result == ForecastFeature.U_WIND_COMPONENT_100_METRE

    def test_from_pb_unknown(self) -> None:
        """Test if the method returns UNSPECIFIED when an unknown value is passed."""
        unknown_pb_value = 999999999  # a random unknown value
        result = ForecastFeature.from_pb(unknown_pb_value)  # type: ignore
        assert result == ForecastFeature.UNSPECIFIED

    def test_from_pb_warning_logged(self, caplog: LogCaptureFixture) -> None:
        """Test if a warning is logged when an unknown value is passed.

        Args:
            caplog: pytest fixture to capture log messages.

        """
        unknown_pb_value = 999999999  # a random unknow value
        ForecastFeature.from_pb(unknown_pb_value)  # type: ignore
        assert "Unknown forecast feature" in caplog.text

    def test_from_pb_valid_enum(self) -> None:
        """Test if the method works correctly when an enum value is passed."""
        forecast_feature_enum_value = ForecastFeature.V_WIND_COMPONENT_100_METRE.value
        result = ForecastFeature.from_pb(forecast_feature_enum_value)
        assert result == ForecastFeature.V_WIND_COMPONENT_100_METRE


class TestLocation:
    """Testing the Location type."""

    def test_from_pb(self) -> None:
        """Test if the inititlization method from proto works correctly."""
        # Create a LocationProto object
        location_proto = LocationProto(latitude=42.0, longitude=18.0, country_code="US")
        result = Location.from_pb(location_proto)

        assert result.latitude == 42.0
        assert result.longitude == 18.0
        assert result.country_code == "US"

    def test_to_pb(self) -> None:
        """Test if the to_pb method works correctly."""
        # Create a Location object
        location = Location(latitude=37.0, longitude=-122.0, country_code="CA")
        result = location.to_pb()

        assert result.latitude == 37.0
        assert result.longitude == -122.0
        assert result.country_code == "CA"

    def test_round_trip(self) -> None:
        """Test if the round trip from Location to proto and back works correctly."""
        # Create a Location object
        original_location = Location(latitude=37.0, longitude=-122.0, country_code="CA")
        location_proto = original_location.to_pb()
        result_location = Location.from_pb(location_proto)

        assert result_location.latitude == original_location.latitude
        assert result_location.longitude == original_location.longitude
        assert result_location.country_code == original_location.country_code


@fixture
def forecastdata() -> (  # pylint: disable=too-many-locals
    tuple[weather_pb2.ReceiveLiveWeatherForecastResponse, int, int, int]
):
    """Create a example ReceiveLiveWeatherForecastResponse proto object.

    Returns: tuple of example ReceiveLiveWeatherForecastResponse proto object,
    number of times, number of locations, number of features
    """
    # Create a list of FeatureForecast objects (replace with actual FeatureForecast objects)
    feature_forecasts_list = []
    some_feature_values = [
        weather_pb2.ForecastFeature.FORECAST_FEATURE_U_WIND_COMPONENT_100_METRE,
        weather_pb2.ForecastFeature.FORECAST_FEATURE_V_WIND_COMPONENT_100_METRE,
        weather_pb2.ForecastFeature.FORECAST_FEATURE_SURFACE_SOLAR_RADIATION_DOWNWARDS,
    ]
    some_float_values = [100, 200, 300]

    for feature, value in zip(some_feature_values, some_float_values):
        forecast = weather_pb2.LocationForecast.Forecasts.FeatureForecast(
            feature=feature, value=value
        )
        feature_forecasts_list.append(forecast)

    many_forecasts = []

    # adding different valid_ts into valid_ts_list

    valid_ts1 = Timestamp()
    valid_ts1.FromJsonString("2024-01-01T01:00:00Z")

    valid_ts2 = Timestamp()
    valid_ts2.FromJsonString("2024-01-01T02:00:00Z")

    valid_ts3 = Timestamp()
    valid_ts3.FromJsonString("2024-01-01T03:00:00Z")

    valid_ts_list = [valid_ts1, valid_ts2, valid_ts3]

    # adding same forecast for different valid_ts into many_forecasts

    for valid_ts in valid_ts_list:
        full_features_forecasts = weather_pb2.LocationForecast.Forecasts(
            valid_at_ts=valid_ts, features=feature_forecasts_list
        )
        many_forecasts.append(full_features_forecasts)

    some_locations_forecasts = []

    some_creation_ts = Timestamp()
    some_creation_ts.FromJsonString("2024-01-01T00:00:00Z")

    # adding different locations into locations_list
    locations = [
        LocationProto(latitude=42.0, longitude=18.0, country_code="US"),
        LocationProto(latitude=43.0, longitude=19.0, country_code="CA"),
    ]

    for location in locations:
        location_forecast = weather_pb2.LocationForecast(
            forecasts=many_forecasts,
            location=location,
            creation_ts=some_creation_ts,
        )
        some_locations_forecasts.append(location_forecast)

    # creating a ReceiveLiveWeatherForecastResponse proto object
    forecasts_proto = weather_pb2.ReceiveLiveWeatherForecastResponse(
        location_forecasts=some_locations_forecasts
    )

    num_times = 3
    num_locations = 2
    num_features = 3

    return forecasts_proto, num_times, num_locations, num_features


class TestForecasts:
    """Testing the Forecasts type.

    Attributes:
        forecasts_proto: example ReceiveLiveWeatherForecastResponse proto object
        num_times: number of times in the example proto object
        num_locations: number of locations in the example proto object
        num_features: number of features in the example proto object

    """

    def test_from_pb(
        self,
        forecastdata: tuple[
            weather_pb2.ReceiveLiveWeatherForecastResponse, int, int, int
        ],
    ) -> None:
        """Test if the inititlization method from proto works correctly."""
        # creating a Forecasts object

        forecasts_proto, num_times, num_locations, num_features = forecastdata
        forecasts = Forecasts.from_pb(forecasts_proto)

        assert forecasts is not None

        # forecast is created from the example proto object

    def test_to_ndarray_vlf_with_no_parameters(
        self,
        forecastdata: tuple[
            weather_pb2.ReceiveLiveWeatherForecastResponse, int, int, int
        ],
    ) -> None:
        """Test if the to_ndarray method works correctly when no filter parameters are passed."""
        # create an example Forecasts object
        forecasts_proto, num_times, num_locations, num_features = forecastdata
        forecasts = Forecasts.from_pb(forecasts_proto)

        # checks if output is a numpy array and matches expected shape
        array = forecasts.to_ndarray_vlf()
        assert isinstance(array, np.ndarray)
        assert array.shape == (
            num_times,
            num_locations,
            num_features,
        )
        assert array[0, 0, 0] == 100

    def test_to_ndarray_vlf_with_some_parameters(
        self,
        forecastdata: tuple[
            weather_pb2.ReceiveLiveWeatherForecastResponse, int, int, int
        ],
    ) -> None:
        """Test if the to_ndarray method works correctly when some filter parameters are passed."""
        # create an example Forecasts object with 3 times, 2 locations and 3 features
        forecasts_proto, num_times, num_locations, num_features = forecastdata
        forecasts = Forecasts.from_pb(forecasts_proto)

        validity_times = [timedelta(hours=2), timedelta(hours=1)]
        locations = [Location(latitude=42.0, longitude=18.0, country_code="US")]
        features = [
            ForecastFeature.V_WIND_COMPONENT_100_METRE,
            ForecastFeature.U_WIND_COMPONENT_100_METRE,
        ]

        array = forecasts.to_ndarray_vlf(
            validity_times=validity_times, locations=locations, features=features
        )

        # checks if output is a numpy array and matches expected shape
        assert isinstance(array, np.ndarray)
        assert array.shape == (len(validity_times), len(locations), len(features))
        assert array[0, 0, 0] == 200

    def test_to_ndarray_vlf_with_all_parameters(
        self,
        forecastdata: tuple[
            weather_pb2.ReceiveLiveWeatherForecastResponse, int, int, int
        ],
    ) -> None:
        """Test if the to_ndarray method works correctly when all filter parameters are passed."""
        # create an example Forecasts object with 3 times, 2 locations and 3 features
        forecasts_proto, num_times, num_locations, num_features = forecastdata
        forecasts = Forecasts.from_pb(forecasts_proto)

        validity_times = [timedelta(hours=3), timedelta(hours=1)]
        locations = [
            Location(latitude=42.0, longitude=18.0, country_code="US"),
            Location(latitude=43.0, longitude=19.0, country_code="CA"),
        ]

        features = [
            ForecastFeature.U_WIND_COMPONENT_100_METRE,
            ForecastFeature.V_WIND_COMPONENT_100_METRE,
            ForecastFeature.SURFACE_SOLAR_RADIATION_DOWNWARDS,
        ]

        array = forecasts.to_ndarray_vlf(
            validity_times=validity_times, locations=locations, features=features
        )

        # checks if output is a numpy array and matches expected shape
        assert isinstance(array, np.ndarray)
        assert array.shape == (len(validity_times), len(locations), len(features))

    def test_to_ndarray_vlf_with_missing_parameters(
        self,
        forecastdata: tuple[
            weather_pb2.ReceiveLiveWeatherForecastResponse, int, int, int
        ],
    ) -> None:
        """Test if the to_ndarray method works correctly when filter parameters are missing."""
        # create an example Forecasts object with 3 times, 2 locations and 3 features
        forecasts_proto, num_times, num_locations, num_features = forecastdata
        forecasts = Forecasts.from_pb(forecasts_proto)

        validity_times = [timedelta(hours=1), timedelta(hours=2), timedelta(days=1)]
        locations = [
            Location(latitude=50.0, longitude=18.0, country_code="US"),
            Location(latitude=43.0, longitude=19.0, country_code="CA"),
        ]

        features = [
            ForecastFeature.U_WIND_COMPONENT_100_METRE,
            ForecastFeature.V_WIND_COMPONENT_100_METRE,
            ForecastFeature.SURFACE_SOLAR_RADIATION_DOWNWARDS,
            ForecastFeature.SURFACE_NET_SOLAR_RADIATION,
        ]

        array = forecasts.to_ndarray_vlf(
            validity_times=validity_times, locations=locations, features=features
        )

        # checks if output is a numpy array and matches expected shape
        assert isinstance(array, np.ndarray)
        assert array.shape == (
            len(validity_times) - 1,
            len(locations) - 1,
            len(features) - 1,
        )
