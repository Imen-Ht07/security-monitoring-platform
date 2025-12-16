"""
Log parsing utilities for CSV and JSON formats.

This module provides functions to parse security logs from CSV and JSON formats,
with support for validation and error handling.
"""

import csv
import json
import logging
from io import StringIO
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class LogParserError(Exception):
    """Base exception for log parsing errors."""
    pass


class CSVParseError(LogParserError):
    """Exception raised when CSV parsing fails."""
    pass


class JSONParseError(LogParserError):
    """Exception raised when JSON parsing fails."""
    pass


def parse_csv_logs(content: str, delimiter: str = ',') -> List[Dict[str, Any]]:
    """
    Parse CSV-formatted log content into a list of dictionaries.
    
    Args:
        content: CSV content as a string
        delimiter: Field delimiter (default: comma)
        
    Returns:
        List of dictionaries, where each dictionary represents a log entry
        
    Raises:
        CSVParseError: If CSV parsing fails or content is invalid
        
    Example:
        >>> csv_content = "timestamp,level,message\\n2025-12-16 12:00:00,INFO,Test log"
        >>> logs = parse_csv_logs(csv_content)
        >>> logs[0]['level']
        'INFO'
    """
    if not content or not isinstance(content, str):
        raise CSVParseError("Content must be a non-empty string")
    
    try:
        logs = []
        csv_file = StringIO(content)
        reader = csv.DictReader(csv_file, delimiter=delimiter)
        
        if reader.fieldnames is None:
            raise CSVParseError("CSV file is empty or has no header row")
        
        for row_num, row in enumerate(reader, start=2):
            if row is None or all(value is None for value in row.values()):
                continue
            logs.append(row)
        
        logger.info(f"Successfully parsed {len(logs)} CSV log entries")
        return logs
        
    except csv.Error as e:
        raise CSVParseError(f"Failed to parse CSV: {str(e)}")
    except Exception as e:
        raise CSVParseError(f"Unexpected error parsing CSV: {str(e)}")


def parse_json_logs(content: str) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Parse JSON-formatted log content.
    
    Supports both:
    - JSON array: [{"log": "entry1"}, {"log": "entry2"}]
    - JSON lines: Lines with individual JSON objects (one per line)
    - Single JSON object
    
    Args:
        content: JSON content as a string
        
    Returns:
        Parsed JSON as a dictionary or list of dictionaries
        
    Raises:
        JSONParseError: If JSON parsing fails or content is invalid
        
    Example:
        >>> json_content = '[{"timestamp": "2025-12-16 12:00:00", "level": "INFO"}]'
        >>> logs = parse_json_logs(json_content)
        >>> logs[0]['level']
        'INFO'
    """
    if not content or not isinstance(content, str):
        raise JSONParseError("Content must be a non-empty string")
    
    try:
        # Try parsing as standard JSON first
        return json.loads(content)
        
    except json.JSONDecodeError:
        # Try parsing as JSON lines (newline-delimited JSON)
        try:
            logs = []
            for line_num, line in enumerate(content.strip().split('\n'), start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON line {line_num}: {str(e)}")
                    raise JSONParseError(f"Invalid JSON on line {line_num}: {str(e)}")
            
            if logs:
                logger.info(f"Successfully parsed {len(logs)} JSON log entries (JSONL format)")
                return logs
            else:
                raise JSONParseError("No valid JSON lines found in content")
                
        except JSONParseError:
            raise
        except Exception as e:
            raise JSONParseError(f"Failed to parse JSON: {str(e)}")


def validate_log_entry(entry: Dict[str, Any], required_fields: Optional[List[str]] = None) -> bool:
    """
    Validate a log entry against required fields.
    
    Args:
        entry: Log entry dictionary to validate
        required_fields: List of required field names. If None, no validation is performed.
        
    Returns:
        True if validation passes
        
    Raises:
        ValueError: If required fields are missing
        
    Example:
        >>> log = {"timestamp": "2025-12-16 12:00:00", "level": "INFO", "message": "Test"}
        >>> validate_log_entry(log, ["timestamp", "level"])
        True
    """
    if not isinstance(entry, dict):
        raise ValueError("Log entry must be a dictionary")
    
    if required_fields:
        missing_fields = [field for field in required_fields if field not in entry]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    return True


def parse_logs(
    content: str,
    format_type: str = 'auto',
    delimiter: str = ',',
    required_fields: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Parse logs from content, automatically detecting format or using specified format.
    
    Args:
        content: Log content as a string
        format_type: Format type - 'csv', 'json', 'jsonl', or 'auto' (default: 'auto')
        delimiter: CSV delimiter (only used for CSV format)
        required_fields: List of required fields in each log entry
        
    Returns:
        List of parsed log entries as dictionaries
        
    Raises:
        LogParserError: If parsing fails with any format
        
    Example:
        >>> content = "timestamp,level,message\\n2025-12-16 12:00:00,INFO,Test"
        >>> logs = parse_logs(content, format_type='csv')
        >>> len(logs)
        1
    """
    if not content or not isinstance(content, str):
        raise LogParserError("Content must be a non-empty string")
    
    content = content.strip()
    logs = []
    
    # Determine format
    if format_type == 'auto':
        # Try to detect format based on content
        if content.startswith('[') or content.startswith('{'):
            format_type = 'json'
        else:
            format_type = 'csv'
    
    # Parse based on format
    try:
        if format_type == 'csv':
            logs = parse_csv_logs(content, delimiter=delimiter)
        elif format_type in ('json', 'jsonl'):
            result = parse_json_logs(content)
            logs = result if isinstance(result, list) else [result]
        else:
            raise LogParserError(f"Unknown format type: {format_type}")
    
    except LogParserError:
        raise
    except Exception as e:
        raise LogParserError(f"Failed to parse logs: {str(e)}")
    
    # Validate entries if required
    if required_fields and logs:
        for idx, log in enumerate(logs):
            try:
                validate_log_entry(log, required_fields)
            except ValueError as e:
                logger.warning(f"Validation failed for entry {idx + 1}: {str(e)}")
    
    return logs


def filter_logs_by_level(logs: List[Dict[str, Any]], level: str) -> List[Dict[str, Any]]:
    """
    Filter log entries by severity level.
    
    Args:
        logs: List of log entries
        level: Severity level to filter by (e.g., 'ERROR', 'WARNING', 'INFO')
        
    Returns:
        Filtered list of log entries
        
    Example:
        >>> logs = [{"level": "ERROR"}, {"level": "INFO"}]
        >>> filtered = filter_logs_by_level(logs, "ERROR")
        >>> len(filtered)
        1
    """
    return [log for log in logs if log.get('level', '').upper() == level.upper()]


def filter_logs_by_date_range(
    logs: List[Dict[str, Any]],
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    date_field: str = 'timestamp'
) -> List[Dict[str, Any]]:
    """
    Filter log entries by date range.
    
    Args:
        logs: List of log entries
        start_date: Start date (inclusive). If None, no lower bound.
        end_date: End date (inclusive). If None, no upper bound.
        date_field: Field name containing the date (default: 'timestamp')
        
    Returns:
        Filtered list of log entries
        
    Example:
        >>> logs = [{"timestamp": "2025-12-16 12:00:00"}]
        >>> start = datetime(2025, 12, 15)
        >>> end = datetime(2025, 12, 17)
        >>> filtered = filter_logs_by_date_range(logs, start, end)
    """
    filtered = []
    
    for log in logs:
        if date_field not in log:
            continue
        
        try:
            # Try to parse the date string
            log_date_str = log[date_field]
            # Try common date formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%d/%m/%Y']:
                try:
                    log_date = datetime.strptime(log_date_str, fmt)
                    break
                except ValueError:
                    continue
            else:
                logger.warning(f"Could not parse date: {log_date_str}")
                continue
            
            # Apply date range filters
            if start_date and log_date < start_date:
                continue
            if end_date and log_date > end_date:
                continue
            
            filtered.append(log)
            
        except Exception as e:
            logger.warning(f"Error filtering log by date: {str(e)}")
            continue
    
    return filtered
