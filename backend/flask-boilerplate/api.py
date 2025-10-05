# -*- coding: utf-8 -*-
from __future__ import annotations

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time
import base64
import os

import requests
from flask import Blueprint, jsonify, request

# Blueprint that app.py registers under /judge
api = Blueprint("api", __name__)

# ------------------------------------------------------------------------------
# Judge0 configuration
# ------------------------------------------------------------------------------

# app = Flask(__name__)
# CORS(app)

# Judge0 Configuration
JUDGE0_URL = os.getenv('JUDGE0_URL', 'https://judge0-ce.p.rapidapi.com')
JUDGE0_API_KEY = os.getenv('JUDGE0_API_KEY', 'cf076a4ac8msh7a6c69e8180223fp1cd086jsn91c117421926')

JUDGE0_HEADERS = {
    'content-type': 'application/json',
    'X-RapidAPI-Key': JUDGE0_API_KEY,
    'X-RapidAPI-Host': 'judge0-ce.p.rapidapi.com'
}

# Language ID mapping for Judge0
LANGUAGE_IDS = {
    'python': 71,  # Python 3
    'javascript': 63,  # JavaScript (Node.js)
    'java': 62,  # Java
    'cpp': 54,  # C++ (GCC 9.2.0)
    'c': 50,  # C (GCC 9.2.0)
    'go': 60,  # Go
    'rust': 73,  # Rust
}


def encode_base64(text):
    """Encode text to base64"""
    return base64.b64encode(text.encode()).decode()


def decode_base64(text):
    """Decode base64 to text"""
    if text:
        return base64.b64decode(text).decode()
    return ""


# python
@api.route('/submit', methods=['POST'])
def submit_code():
    """
    Submit code to run against test cases.

    Expected JSON body (Python):
    {
        "code": "<user source code that defines the entry point>",
        "language": "python",
        "problem_id": "two-sum",       # optional, used to derive entry_point if not provided
        "entry_point": "twoSum",       # optional, recommended
        "test_cases": [
            # Any of the following shapes:
            {"input": {"args": [[2,7,11,15], 9]}, "expected_output": "[0,1]"},
            {"input": {"kwargs": {"nums": [2,7,11,15], "target": 9}}, "expected_output": "[0,1]"},
            {"args": [[2,7,11,15], 9], "expected_output": [0,1]},
            {"kwargs": {"nums": [3,2,4], "target": 6}, "expected_output": [1,2]},
            # Or with "input" as a JSON string:
            {"input": "{\"args\": [[2,7,11,15], 9]}", "expected_output": "[0,1]"}
        ]
    }
    """
    import json
    import time
    from typing import Any, Dict, Tuple

    # Helper: derive entry point name from problem_id (e.g., "two-sum" -> "twoSum")
    def _derive_entry_point(problem_id: str | None) -> str | None:
        if not problem_id:
            return None
        parts = [p for p in str(problem_id).replace('_', '-').split('-') if p]
        if not parts:
            return None
        first, *rest = parts
        return first.lower() + ''.join(s.capitalize() for s in rest)

    # Helper: harness that reads stdin JSON {args, kwargs}, calls entry point, prints JSON
    def _python_harness(entry_point: str) -> str:
        return f"""
import sys, json
def __runner():
    raw = sys.stdin.read()
    payload = {{}}
    if raw:
        try:
            payload = json.loads(raw)
        except Exception:
            print("__HARNESS_INPUT_ERROR__", file=sys.stderr)
            return
    args = payload.get("args") or []
    kwargs = payload.get("kwargs") or {{}}
    try:
        result = {entry_point}(*args, **kwargs)
    except Exception as e:
        # Surface runtime errors to stderr so your API can show them
        print(str(e), file=sys.stderr)
        return
    # Stable, whitespace-free JSON for reliable comparison
    print(json.dumps(result, separators=(",", ":")))
if __name__ == "__main__":
    __runner()
""".lstrip()

    # Helper: parse a single test case into (args, kwargs)
    def _parse_case_io(tc: Dict[str, Any]) -> Tuple[list, dict, str | None]:
        """
        Returns (args, kwargs, parse_error)
        Accepts:
          - tc["args"] list
          - tc["kwargs"] dict
          - tc["input"] dict with optional args/kwargs
          - tc["input"] JSON string -> dict/list
          - tc["input"] list -> args
          - tc["input"] dict without args/kwargs -> kwargs
        """
        args, kwargs = [], {}
        if "args" in tc:
            if not isinstance(tc["args"], list):
                return [], {}, "args must be a list"
            args = tc["args"]
        if "kwargs" in tc:
            if not isinstance(tc["kwargs"], dict):
                return [], {}, "kwargs must be a dict"
            kwargs = tc["kwargs"]

        if "input" in tc and (not args and not kwargs):
            inp = tc["input"]
            # If input is a string, try to parse as JSON
            if isinstance(inp, str):
                try:
                    inp = json.loads(inp)
                except Exception:
                    return [], {}, "input must be JSON when provided as a string"
            # If input is a list -> positional args
            if isinstance(inp, list):
                args = inp
            # If input is a dict
            elif isinstance(inp, dict):
                if "args" in inp or "kwargs" in inp:
                    iargs = inp.get("args") or []
                    ikw = inp.get("kwargs") or {}
                    if not isinstance(iargs, list) or not isinstance(ikw, dict):
                        return [], {}, "input.args must be list and input.kwargs must be dict"
                    args, kwargs = iargs, ikw
                else:
                    # Treat entire dict as kwargs
                    kwargs = inp
            else:
                return [], {}, "input must be a list or object (or JSON string for one of those)"

        return args, kwargs, None

    # Helper: normalize expected_output to the exact JSON string our harness prints
    def _normalize_expected(expected: Any) -> Tuple[str | None, str | None]:
        """
        Returns (normalized_string, error_message)
        Accepts Python values directly, or strings that are JSON; falls back
        to treating a non-JSON string as a literal string value.
        """
        try:
            # If it's a string, try to parse it as JSON
            if isinstance(expected, str):
                try:
                    val = json.loads(expected)
                except Exception:
                    # Treat as a raw string expected value
                    val = expected
            else:
                val = expected
            return json.dumps(val, separators=(",", ":")), None
        except Exception:
            return None, "expected_output could not be normalized to JSON"

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON body"}), 400

    code = data.get('code')
    language = (data.get('language') or 'python').lower()
    test_cases = data.get('test_cases', [])
    problem_id = data.get('problem_id')
    entry_point = data.get('entry_point') or _derive_entry_point(problem_id)

    # Basic validations
    if not isinstance(code, str) or not code.strip():
        return jsonify({'error': 'Code is required'}), 400
    if not isinstance(test_cases, list) or not test_cases:
        return jsonify({'error': 'Test cases are required'}), 400
    if language != 'python':
        return jsonify({'error': f'Unsupported language: {language}. Only "python" is supported currently.'}), 400

    language_id = LANGUAGE_IDS.get('python')
    if not language_id:
        return jsonify({'error': 'Server misconfiguration: Python language not available'}), 500

    # Build full source with harness
    # If no entry_point could be derived, use a conventional default (will error at runtime if missing).
    entry_point = entry_point or 'solve'
    full_code_prefix = f"{code.rstrip()}\n\n{_python_harness(entry_point)}"

    results = []
    all_passed = True

    # Timeouts and polling settings
    connect_timeout = 5   # seconds
    read_timeout = 30     # seconds
    poll_sleep = 0.5      # seconds
    max_polls = int(read_timeout / poll_sleep)

    for i, test_case in enumerate(test_cases):
        # Parse IO
        args, kwargs, io_error = _parse_case_io(test_case if isinstance(test_case, dict) else {})
        expected_raw = (test_case or {}).get('expected_output') if isinstance(test_case, dict) else None

        if io_error:
            results.append({
                'test_case': i + 1,
                'status': 'error',
                'input': test_case,
                'error': f'Invalid test case input: {io_error}',
                'passed': False
            })
            all_passed = False
            continue

        # Normalize expected output into the JSON string our harness prints
        normalized_expected, norm_err = _normalize_expected(expected_raw)
        if norm_err:
            results.append({
                'test_case': i + 1,
                'status': 'error',
                'input': test_case,
                'error': norm_err,
                'passed': False
            })
            all_passed = False
            continue

        # Submission payload
        stdin_payload = {"args": args, "kwargs": kwargs}
        submission = {
            'source_code': encode_base64(full_code_prefix),
            'language_id': language_id,
            'stdin': encode_base64(json.dumps(stdin_payload, separators=(",", ":"))),
            'expected_output': encode_base64(normalized_expected),
        }

        try:
            # Create submission (wait=true often returns final result, but we still verify status)
            response = requests.post(
                f'{JUDGE0_URL}/submissions',
                json=submission,
                headers=JUDGE0_HEADERS,
                params={'base64_encoded': 'true', 'wait': 'true'},
                timeout=(connect_timeout, read_timeout)
            )

            if response.status_code not in (200, 201):
                results.append({
                    'test_case': i + 1,
                    'status': 'error',
                    'input': test_case,
                    'error': f'Judge0 API error: {response.status_code}',
                    'passed': False
                })
                all_passed = False
                continue

            result = response.json()
            token = result.get('token')

            # Ensure terminal status via polling
            status_id = (result.get('status') or {}).get('id')
            polls = 0
            while status_id in (1, 2) and polls < max_polls and token:
                time.sleep(poll_sleep)
                polls += 1
                result_response = requests.get(
                    f'{JUDGE0_URL}/submissions/{token}',
                    headers=JUDGE0_HEADERS,
                    params={'base64_encoded': 'true'},
                    timeout=(connect_timeout, read_timeout)
                )
                if result_response.status_code not in (200, 201):
                    break
                result = result_response.json()
                status_id = (result.get('status') or {}).get('id')

            # Decode outputs
            stdout = (decode_base64(result.get('stdout', '') or '')).strip()
            stderr = (decode_base64(result.get('stderr', '') or '')).strip()
            compile_output = (decode_base64(result.get('compile_output', '') or '')).strip()
            status_desc = (result.get('status') or {}).get('description', 'Unknown')

            # Determine pass/fail based on Judge0 status (3 == Accepted)
            if status_id == 3:
                passed = True
                results.append({
                    'test_case': i + 1,
                    'status': 'passed',
                    'input': stdin_payload,
                    'expected_output': normalized_expected,
                    'actual_output': stdout,
                    'passed': True,
                    'execution_time': result.get('time'),
                    'memory': result.get('memory')
                })
            elif status_id in (4, 5):  # Wrong Answer, Time Limit Exceeded
                passed = False
                error_msg = None
                results.append({
                    'test_case': i + 1,
                    'status': 'failed',
                    'input': stdin_payload,
                    'expected_output': normalized_expected,
                    'actual_output': stdout,
                    'error': error_msg,
                    'passed': False,
                    'execution_time': result.get('time'),
                    'memory': result.get('memory'),
                    'status_description': status_desc,
                })
                all_passed = False
            else:
                # Compilation or runtime error
                passed = False
                error_msg = stderr or compile_output or status_desc
                results.append({
                    'test_case': i + 1,
                    'status': 'error',
                    'input': stdin_payload,
                    'error': error_msg,
                    'passed': False,
                    'execution_time': result.get('time'),
                    'memory': result.get('memory'),
                    'status_description': status_desc,
                })
                all_passed = False

        except requests.Timeout:
            results.append({
                'test_case': i + 1,
                'status': 'error',
                'input': stdin_payload,
                'error': 'Judge0 request timed out',
                'passed': False
            })
            all_passed = False
        except Exception as e:
            # Avoid leaking internals; return concise error
            results.append({
                'test_case': i + 1,
                'status': 'error',
                'input': stdin_payload if 'stdin_payload' in locals() else None,
                'error': 'Internal error while processing this test case',
                'passed': False
            })
            all_passed = False

    return jsonify({
        'success': all_passed,
        'results': results,
        'total_tests': len(test_cases),
        'passed_tests': sum(1 for r in results if r.get('passed', False))
    })

@api.route('/languages', methods=['GET'])
def get_languages():
    return jsonify({
        'languages': [
            {'id': 'python', 'name': 'Python 3', 'judge0_id': 71},
            {'id': 'javascript', 'name': 'JavaScript (Node.js)', 'judge0_id': 63},
            {'id': 'java', 'name': 'Java', 'judge0_id': 62},
            {'id': 'cpp', 'name': 'C++', 'judge0_id': 54},
            {'id': 'c', 'name': 'C', 'judge0_id': 50},
            {'id': 'go', 'name': 'Go', 'judge0_id': 60},
            {'id': 'rust', 'name': 'Rust', 'judge0_id': 73},
        ]
    })


@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'judge0-api'})