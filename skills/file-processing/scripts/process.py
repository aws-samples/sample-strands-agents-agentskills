"""
Data Processing Utility Functions

This module provides reusable functions for common data processing tasks.
"""

import csv
import json
from io import StringIO
from typing import List, Dict, Any, Callable
from collections import defaultdict
from statistics import mean, median, stdev


def load_csv(content: str, delimiter: str = ',') -> List[Dict[str, str]]:
    """
    Load CSV content into a list of dictionaries.

    Args:
        content: CSV file content as string
        delimiter: Field delimiter (default: comma)

    Returns:
        List of dictionaries, one per row

    Example:
        >>> csv_data = "name,age\\nAlice,30\\nBob,25"
        >>> data = load_csv(csv_data)
        >>> print(data)
        [{'name': 'Alice', 'age': '30'}, {'name': 'Bob', 'age': '25'}]
    """
    reader = csv.DictReader(StringIO(content), delimiter=delimiter)
    return list(reader)


def load_json(content: str) -> Any:
    """
    Load JSON content.

    Args:
        content: JSON file content as string

    Returns:
        Parsed JSON data (dict or list)

    Example:
        >>> json_data = '[{"name": "Alice", "age": 30}]'
        >>> data = load_json(json_data)
        >>> print(data)
        [{'name': 'Alice', 'age': 30}]
    """
    return json.loads(content)


def remove_duplicates(data: List[Dict], key: str = None) -> List[Dict]:
    """
    Remove duplicate rows from data.

    Args:
        data: List of dictionaries
        key: Optional key to determine uniqueness (if None, checks entire row)

    Returns:
        List with duplicates removed

    Example:
        >>> data = [{'id': 1, 'name': 'Alice'}, {'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
        >>> unique = remove_duplicates(data)
        >>> print(len(unique))
        2
    """
    if key:
        seen = set()
        result = []
        for row in data:
            if row.get(key) not in seen:
                seen.add(row.get(key))
                result.append(row)
        return result
    else:
        # Remove duplicates based on entire row
        seen = set()
        result = []
        for row in data:
            row_tuple = tuple(sorted(row.items()))
            if row_tuple not in seen:
                seen.add(row_tuple)
                result.append(row)
        return result


def filter_data(data: List[Dict], condition: Callable[[Dict], bool]) -> List[Dict]:
    """
    Filter data based on a condition function.

    Args:
        data: List of dictionaries
        condition: Function that takes a row and returns True/False

    Returns:
        Filtered list

    Example:
        >>> data = [{'age': 30}, {'age': 25}, {'age': 35}]
        >>> filtered = filter_data(data, lambda row: int(row['age']) >= 30)
        >>> print(len(filtered))
        2
    """
    return [row for row in data if condition(row)]


def select_columns(data: List[Dict], columns: List[str]) -> List[Dict]:
    """
    Select specific columns from data.

    Args:
        data: List of dictionaries
        columns: List of column names to keep

    Returns:
        List with only selected columns

    Example:
        >>> data = [{'name': 'Alice', 'age': 30, 'city': 'NYC'}]
        >>> selected = select_columns(data, ['name', 'age'])
        >>> print(selected)
        [{'name': 'Alice', 'age': 30}]
    """
    return [{col: row.get(col) for col in columns} for row in data]


def sort_data(data: List[Dict], key: str, reverse: bool = False) -> List[Dict]:
    """
    Sort data by a specific column.

    Args:
        data: List of dictionaries
        key: Column name to sort by
        reverse: If True, sort in descending order

    Returns:
        Sorted list

    Example:
        >>> data = [{'name': 'Bob', 'age': 25}, {'name': 'Alice', 'age': 30}]
        >>> sorted_data = sort_data(data, 'age')
        >>> print(sorted_data[0]['name'])
        Bob
    """
    def sort_key(row):
        value = row.get(key)
        # Try to convert to number for numeric sorting
        try:
            return float(value)
        except (ValueError, TypeError):
            return str(value).lower()

    return sorted(data, key=sort_key, reverse=reverse)


def group_by(data: List[Dict], key: str) -> Dict[Any, List[Dict]]:
    """
    Group data by a specific column.

    Args:
        data: List of dictionaries
        key: Column name to group by

    Returns:
        Dictionary mapping group keys to lists of rows

    Example:
        >>> data = [
        ...     {'category': 'A', 'value': 10},
        ...     {'category': 'A', 'value': 20},
        ...     {'category': 'B', 'value': 30}
        ... ]
        >>> grouped = group_by(data, 'category')
        >>> print(len(grouped['A']))
        2
    """
    result = defaultdict(list)
    for row in data:
        result[row.get(key)].append(row)
    return dict(result)


def aggregate(data: List[Dict], group_key: str, value_key: str, operations: List[str] = None) -> List[Dict]:
    """
    Aggregate data by group with specified operations.

    Args:
        data: List of dictionaries
        group_key: Column to group by
        value_key: Column to aggregate
        operations: List of operations ('sum', 'mean', 'median', 'count', 'min', 'max')

    Returns:
        List of aggregated results

    Example:
        >>> data = [
        ...     {'category': 'A', 'amount': 10},
        ...     {'category': 'A', 'amount': 20},
        ...     {'category': 'B', 'amount': 30}
        ... ]
        >>> result = aggregate(data, 'category', 'amount', ['sum', 'mean', 'count'])
        >>> # Returns: [{'category': 'A', 'sum': 30, 'mean': 15, 'count': 2}, {'category': 'B', ...}]
    """
    if operations is None:
        operations = ['sum', 'mean', 'count']

    grouped = group_by(data, group_key)
    results = []

    for group, rows in grouped.items():
        values = [float(row.get(value_key, 0)) for row in rows if row.get(value_key)]

        result = {group_key: group}

        for op in operations:
            if op == 'sum':
                result['sum'] = sum(values)
            elif op == 'mean' or op == 'avg' or op == 'average':
                result['mean'] = mean(values) if values else 0
            elif op == 'median':
                result['median'] = median(values) if values else 0
            elif op == 'count':
                result['count'] = len(values)
            elif op == 'min':
                result['min'] = min(values) if values else None
            elif op == 'max':
                result['max'] = max(values) if values else None
            elif op == 'std' or op == 'stdev':
                result['std'] = stdev(values) if len(values) > 1 else 0

        results.append(result)

    return results


def to_markdown_table(data: List[Dict], columns: List[str] = None) -> str:
    """
    Convert data to markdown table format.

    Args:
        data: List of dictionaries
        columns: Optional list of columns to include (default: all)

    Returns:
        Markdown formatted table string

    Example:
        >>> data = [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]
        >>> table = to_markdown_table(data)
        >>> print(table)
        | name | age |
        | --- | --- |
        | Alice | 30 |
        | Bob | 25 |
    """
    if not data:
        return "No data to display"

    if columns is None:
        columns = list(data[0].keys())

    # Header
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"

    # Rows
    rows = []
    for row in data:
        values = [str(row.get(col, "")) for col in columns]
        row_str = "| " + " | ".join(values) + " |"
        rows.append(row_str)

    return "\n".join([header, separator] + rows)


def to_csv(data: List[Dict], columns: List[str] = None) -> str:
    """
    Convert data to CSV format.

    Args:
        data: List of dictionaries
        columns: Optional list of columns to include (default: all)

    Returns:
        CSV formatted string

    Example:
        >>> data = [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]
        >>> csv = to_csv(data)
        >>> print(csv)
        name,age
        Alice,30
        Bob,25
    """
    if not data:
        return ""

    if columns is None:
        columns = list(data[0].keys())

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    writer.writerows(data)

    return output.getvalue()


def to_json(data: List[Dict], pretty: bool = True) -> str:
    """
    Convert data to JSON format.

    Args:
        data: List of dictionaries
        pretty: If True, format with indentation

    Returns:
        JSON formatted string

    Example:
        >>> data = [{'name': 'Alice', 'age': 30}]
        >>> json_str = to_json(data)
        >>> print(json_str)
    """
    if pretty:
        return json.dumps(data, indent=2)
    else:
        return json.dumps(data)


def describe_data(data: List[Dict], numeric_columns: List[str] = None) -> Dict:
    """
    Generate descriptive statistics for numeric columns.

    Args:
        data: List of dictionaries
        numeric_columns: List of columns to analyze (auto-detect if None)

    Returns:
        Dictionary with statistics

    Example:
        >>> data = [{'age': 30, 'score': 85}, {'age': 25, 'score': 90}]
        >>> stats = describe_data(data, ['age', 'score'])
        >>> print(stats['age']['mean'])
        27.5
    """
    if not data:
        return {}

    if numeric_columns is None:
        # Auto-detect numeric columns
        first_row = data[0]
        numeric_columns = []
        for key, value in first_row.items():
            try:
                float(value)
                numeric_columns.append(key)
            except (ValueError, TypeError):
                pass

    results = {}

    for col in numeric_columns:
        values = []
        for row in data:
            try:
                values.append(float(row.get(col, 0)))
            except (ValueError, TypeError):
                pass

        if values:
            results[col] = {
                'count': len(values),
                'mean': mean(values),
                'median': median(values),
                'min': min(values),
                'max': max(values),
                'std': stdev(values) if len(values) > 1 else 0
            }

    return results
