from typing import Callable, List, Any, TypeVar, Optional

T = TypeVar('T')
def find_matching_indices(lines, filter: Callable[[str], bool]):
    first_index = None
    last_index = None

    # Create a map object containing boolean values
    matches = map(filter, lines)

    # Convert the map object to a list of boolean values
    matches_list = list(matches)

    # Find first index
    try:
        first_index = matches_list.index(True)
    except ValueError:
        pass

    # Find last index
    try:
        last_index = len(matches_list) - 1 - matches_list[::-1].index(True)
    except ValueError:
        pass

    return first_index, last_index

def find_indices(lines:[T], condition_lambda:Callable[[T], bool]) ->[int]:
    matching_indices = [index for index, line in filter(lambda idx_val: condition_lambda(idx_val[1]), enumerate(lines))]
    return matching_indices


def add_missing_indices_sorted(source: List[int], target: List[int]) -> List[int]:
    # Convert target to a set for faster look-up
    target_set = set(target)

    # Add missing elements from source to target
    for elem in source:
        if elem not in target_set:
            target.append(elem)
            target_set.add(elem)

    # Sort the updated target list
    target.sort()

    return target


def merge_number_set(source: List[int], target: List[int]) -> List[int]:

    # Assert that both source and target are sorted
    assert source == sorted(source), "Source list must be sorted"
    assert target == sorted(target), "Target list must be sorted"

    new_target = []
    i, j = 0, 0

    while i < len(source) and j < len(target):
        if source[i] < target[j]:
            new_target.append(source[i])
            i += 1
        elif source[i] > target[j]:
            new_target.append(target[j])
            j += 1
        else:
            new_target.append(source[i])
            i += 1
            j += 1

    # Append any remaining elements in either list
    new_target.extend(source[i:])
    new_target.extend(target[j:])

    return new_target


def find_sequences(sorted_list: [int], min_val: Optional[int] = None, max_val: Optional[int] = None) -> [(int, int)]:
    # Assert that the list is sorted
    assert sorted_list == sorted(sorted_list), "Input list must be sorted"

    sequences = []

    # Handle empty list case
    if not sorted_list:
        return []

    # Initialize 'start' depending on whether min_val is specified
    start = min_val if min_val is not None and sorted_list[0] == min_val else sorted_list[0]

    for i in range(1, len(sorted_list)):
        if sorted_list[i] - sorted_list[i - 1] > 1:
            sequences.append((start, sorted_list[i - 1]))
            start = sorted_list[i]

    # Add the last sequence depending on whether max_val is specified
    end = max_val if max_val is not None and sorted_list[-1] == max_val else sorted_list[-1]
    sequences.append((start, end))

    return sequences