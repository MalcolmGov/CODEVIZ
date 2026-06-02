"""Tests for shared utility functions."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils import (
    format_success_response,
    format_error_response,
    truncate_string,
    safe_json_loads,
    safe_json_dumps,
)


# ── format_success_response ──────────────────────────────────────────────────

def test_success_response_has_status_success():
    body, _ = format_success_response({'key': 'value'})
    assert body['status'] == 'success'


def test_success_response_wraps_data():
    body, _ = format_success_response({'items': [1, 2, 3]})
    assert body['data']['items'] == [1, 2, 3]


def test_success_response_includes_message():
    body, _ = format_success_response({}, message='All good')
    assert body['message'] == 'All good'


def test_success_response_includes_timestamp():
    body, _ = format_success_response({})
    assert 'timestamp' in body


def test_success_response_status_code_is_200():
    _, code = format_success_response({})
    assert code == 200


def test_success_response_data_can_be_none():
    body, code = format_success_response(None)
    assert code == 200
    assert body['data'] is None


# ── format_error_response ────────────────────────────────────────────────────

def test_error_response_has_status_error():
    body, _ = format_error_response('Something broke')
    assert body['status'] == 'error'


def test_error_response_includes_message():
    body, _ = format_error_response('Bad input')
    assert body['message'] == 'Bad input'


def test_error_response_default_code_is_400():
    _, code = format_error_response('oops')
    assert code == 400


def test_error_response_includes_timestamp():
    body, _ = format_error_response('err')
    assert 'timestamp' in body


# ── truncate_string ──────────────────────────────────────────────────────────

def test_truncate_short_string_unchanged():
    assert truncate_string('hello', 100) == 'hello'


def test_truncate_long_string():
    result = truncate_string('a' * 200, 50)
    assert len(result) < 200
    assert result.endswith('...')


def test_truncate_exact_length():
    s = 'a' * 100
    assert truncate_string(s, 100) == s


# ── safe_json_loads ──────────────────────────────────────────────────────────

def test_safe_json_loads_valid():
    assert safe_json_loads('{"a": 1}') == {'a': 1}


def test_safe_json_loads_invalid_returns_default():
    assert safe_json_loads('not json', default={'fallback': True}) == {'fallback': True}


def test_safe_json_loads_passes_dict_through():
    d = {'already': 'parsed'}
    assert safe_json_loads(d) == d


def test_safe_json_loads_none_default_on_invalid():
    result = safe_json_loads('{{bad}}')
    assert result == {}


# ── safe_json_dumps ──────────────────────────────────────────────────────────

def test_safe_json_dumps_valid_dict():
    result = safe_json_dumps({'key': 'val'})
    assert '"key"' in result


def test_safe_json_dumps_handles_non_serialisable():
    from datetime import datetime
    result = safe_json_dumps({'dt': datetime.now()})
    assert result is not None
