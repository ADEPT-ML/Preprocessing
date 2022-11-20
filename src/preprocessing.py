"""Contains all preprocessing function for sensor data"""
import pandas as pd
from dataclasses import dataclass
import json


@dataclass
class Building:
    """Contains all information of a building"""
    @dataclass
    class Sensor:
        """Contains all information to describe a sensor"""
        type: str
        desc: str
        unit: str

    name: str
    sensors: list[Sensor]
    dataframe: pd.DataFrame


def json_to_buildings(data: dict) -> dict:
    """Converts a json representation of a building into a building object.

    :param data: A json representation of a building
    :return: The building object
    """
    buildings = dict()
    for k, b in data.items():
        sensors = [Building.Sensor(s["type"], s["desc"], s["unit"]) for s in b["sensors"]]
        df_json = json.loads(b["dataframe"])
        df = pd.DataFrame(df_json)
        df.index = pd.to_datetime(df.index.values, unit='ms')
        buildings[k] = Building(k, sensors, df)
    return buildings


def interpolate_dict(data: dict[str, Building]) -> None:
    """Interpolates all missing values in the sensor data sets.

    :param data: A dictionary of buildings
    """
    for _, building in data.items():
        building.dataframe.interpolate(method='linear', limit_direction='both', inplace=True)


def remove_nan_dict(data: dict[str, Building]) -> None:
    """Removes all sensor data sets with only NaN values.

    :param data: A dictionary of buildings
    """
    for _, building in data.items():
        building.dataframe.dropna(axis=1, how="all", inplace=True)


def remove_unwanted_rows(data: dict[str, Building], threshold: int) -> None:
    """Removes all sensor data sets with less unique values than the given threshold.

    :param data: A dictionary of buildings
    :param threshold: The minimum amount of unique values
    """
    for _, building in data.items():
        for key in building.dataframe:
            local_list = {e for e in building.dataframe[key] if e == e}
            if len(local_list) < threshold:
                building.dataframe.drop(columns=key, inplace=True)


def remove_empty_buildings(data: dict[str, Building]) -> dict[str, Building]:
    """Removes all buildings that have no sensor data.

    :param data: A dictionary of buildings
    :return: The dictionary without the removed buildings
    """
    return {k: v for k, v in data.items() if len(v.sensors) > 0}


def merge_duplicate_sensors(data: dict[str, Building], threshold: int) -> None:
    """Merges sensors with identical data.

    :param data: A dictionary of buildings
    :param threshold: The threshold for the allowed amount of value mismatches between two similar sensor lists
    """
    for _, building in data.items():
        keys = []
        marked_for_deletion = set()
        for key in building.dataframe:
            keys.append(key)
        for i in range(len(keys)):
            local_list = [e for e in building.dataframe[keys[i]] if e == e]
            for j in range(i + 1, len(keys)):
                local_list_two = [e for e in building.dataframe[keys[j]] if e == e]
                if len(local_list) != len(local_list_two):
                    continue
                if local_list == local_list_two:
                    marked_for_deletion.add(keys[j])
                else:
                    diff_entries = [(local_list[c], local_list_two[c]) for c in range(len(local_list)) if
                                    local_list[c] != local_list_two[c]]
                    if len(diff_entries) < threshold:
                        marked_for_deletion.add(keys[j])
        for key in marked_for_deletion:
            building.dataframe.drop(columns=key, inplace=True)


def remove_leftover_sensors(data: dict[str, Building]) -> None:
    """Removes all sensors from the given buildings that do not have data.

    :param data: A dictionary of buildings
    """
    for _, building in data.items():
        building.sensors = [s for s in building.sensors if s.type in building.dataframe.keys()]


def min_max_normalization(df) -> pd.DataFrame:
    """Normalizes all data in the dataframe to a range from 0 to 1.

    :param df: The dataframe to normalize
    :return: The normalized dataframe
    """
    return (df - df.min()) / (df.max() - df.min())


def mean_normalization(df) -> pd.DataFrame:
    """Normalizes all data in the dataframe into a standard score.

    :param df: The dataframe to normalize
    :return: The normalized dataframe
    """
    return (df - df.mean()) / df.std()
