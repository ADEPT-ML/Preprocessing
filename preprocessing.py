import pandas as pd
from dataclasses import dataclass
import json

@dataclass
class Building:
    @dataclass
    class Sensor:
        type: str
        desc: str
        unit: str

    name: str
    sensors: list[Sensor]
    dataframe: pd.DataFrame

def json_to_buildings(data: dict) -> dict:
    buildings = dict()
    for k, b in data.items():
        sensors = [Building.Sensor(s["type"], s["desc"], s["unit"]) for s in b["sensors"]]
        buildings[k] = Building(k, sensors, pd.DataFrame(json.loads(b["dataframe"])))
    return buildings

def interpolate_dict(data: dict[str, Building]) -> None:
    for _, building in data.items():
        building.dataframe.interpolate(method='linear', limit_direction='both', inplace=True)


def remove_nan_dict(data: dict[str, Building]) -> None:
    for _, building in data.items():
        building.dataframe.dropna(axis=1, how="all", inplace=True)


def remove_unwanted_rows(data: dict[str, Building], threshold: int) -> None:
    for _, building in data.items():
        for key in building.dataframe:
            local_list = {e for e in building.dataframe[key] if e == e}
            if len(local_list) < threshold:
                building.dataframe.drop(columns=key, inplace=True)


def remove_empty_buildings(data: dict[str, Building]) -> dict[str, Building]:
    return {k: v for k, v in data.items() if len(v.sensors) > 0}


def merge_duplicate_sensors(data: dict[str, Building]) -> None:
    for _, building in data.items():
        keys = []
        marked_for_deletion = set()
        for key in building.dataframe:
            keys.append(key)
        for i in range(len(keys)):
            local_list = [e for e in building.dataframe[keys[i]] if e == e]
            for j in range(i + 1, len(keys)):
                local_list_two = [e for e in building.dataframe[keys[j]] if e == e]
                if len(local_list) != local_list_two:
                    continue
                if local_list == local_list_two:
                    marked_for_deletion.add(keys[j])
                else:
                    if building.name == "EF 40a":
                        print("Comparing", keys[i], keys[j])
                        diff_entries = [(local_list[c], local_list_two[c]) for c in range(len(local_list)) if local_list[c] != local_list_two[c]]
                        if len(diff_entries) < 100:
                            print(diff_entries)
        for key in marked_for_deletion:
            building.dataframe.drop(columns=key, inplace=True)


def remove_leftover_sensors(data: dict[str, Building]) -> None:
    for _, building in data.items():
        building.sensors = [s for s in building.sensors if s.type in building.dataframe.keys()]


def min_max_normalization(df) -> pd.DataFrame:
    return (df - df.min()) / (df.max() - df.min())


def mean_normalization(df) -> pd.DataFrame:
    return (df - df.mean()) / df.std()
