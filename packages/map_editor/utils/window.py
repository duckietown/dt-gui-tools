from os import listdir
from os.path import join
from typing import List
from utils.constants import TRAFFIC_SIGNS_TYPES_IDS


def get_id_by_type(type_of_obj: str, existing_ids: List[int]) -> int:
    all_ids = TRAFFIC_SIGNS_TYPES_IDS[type_of_obj]
    free_ids = get_free_ids_by_type(existing_ids, all_ids)
    if len(free_ids):
        return free_ids[0]
    else:
        return all_ids[-1]


def get_free_ids_by_type(existing_ids: List[int], all_ids: List[int] = None) -> List[int]:
    return [id_ for id_ in all_ids if (id_ not in existing_ids)]


def get_list_dir(dir_path):
    try:
        entries = listdir(dir_path)
        return entries
    except FileNotFoundError as e:
        return []


def get_list_dir_with_path(dir_path): return [(filename, join(dir_path, filename)) for filename in
                                              get_list_dir(dir_path)]


def get_available_translations(lang_dir_path): return {filename[len('lang_'):-len('.qm')]: path for filename, path in
                                                       get_list_dir_with_path(lang_dir_path)}
