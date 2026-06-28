# Codebase Review: py-aqi-in-api

**Review Date:** 2026-06-28
**Package:** AQI.in Python SDK (v0.1.0)
**Source:** Python port of [aqi-in-api](https://github.com/neo773/aqi-in-api) TypeScript SDK

---

## Overview

Well-structured, modern Python SDK using `httpx`, `dataclasses`, and `pyjwt`. Fully typed with mypy strict mode, 90% test coverage, clean ruff linting. Good foundation with clear separation of concerns.

**Overall Health:** GOOD with room for polish.

---

## Automated Check Results

| Check | Status | Details |
|-------|--------|---------|
| Ruff (extended) | 125 warnings | Most are docstrings (`D`), assert-in-test (`S101`), `Any` annotations (`ANN401`) |
| Mypy (strict) | ✅ PASS | 0 errors across 11 files |
| Pytest (24 tests) | ✅ PASS | 24/24 pass, 90% coverage |
| Bandit | 1 finding | Hardcoded password `"masai"` in `_token.py:5` |
| PyJWT | 13 warnings | `InsecureKeyLengthWarning` - 5-byte HMAC key |

---

## Detailed Findings

### 🔴 High Priority

#### H1. Missing `py.typed` marker file
- **File:** `src/aqi_in_api/` (missing)
- **Issue:** PEP 561 compliance. Without `py.typed`, external consumers won't get type information even though the package is fully typed.
- **Fix:** Add empty `py.typed` file to the package directory.

#### H2. Hardcoded JWT secret triggers Bandit and PyJWT warnings
- **File:** `src/aqi_in_api/_token.py:5`
- **Issue:** `JWT_SECRET = "masai"` is hardcoded. Bandit flags it (B105), PyJWT warns about insecure key length (5 bytes vs. 32 minimum).
- **Context:** Intentional — replicating TS SDK behavior. The API server validates tokens signed with this exact secret.
- **Fix:** Suppress Bandit via `# nosec`; filter PyJWT warning in test config.

#### H3. No httpx timeout configured
- **File:** `src/aqi_in_api/_client.py:86`
- **Issue:** `httpx.AsyncClient()` created without timeout, meaning HTTP requests can hang indefinitely on slow/unstable networks.
- **Fix:** Add a sensible default timeout (e.g., 30s).

#### H4. Dependabot missing versioning strategy
- **File:** `.github/dependabot.yml`
- **Issue:** `pip` ecosystem configured without `versioning-strategy`, which means Dependabot may pin to any version satisfying the semver range instead of using a consistent strategy.
- **Fix:** Add `versioning-strategy: increase-if-necessary` or `lockfile-only`.

### 🟡 Medium Priority

#### M1. Missing `__all__` in `models.py`
- **File:** `src/aqi_in_api/models.py`
- **Issue:** `models.py` is a public module (no underscore prefix) but lacks `__all__`. All 15+ classes are implicitly exported.
- **Fix:** Add explicit `__all__`.

#### M2. Mypy and pytest-cov not in pyproject.toml dev deps
- **File:** `pyproject.toml`
- **Issue:** Missing from `[dependency-groups.dev]`. Relied on being globally installed or resolvable by the CI runner's env.
- **Fix:** Add `mypy>=2.1.0` and `pytest-cov>=7.1.0` to dev dependencies.

#### M3. `example.py` doesn't close the client
- **File:** `example.py`
- **Issue:** No `await client.close()` at the end of `main()`. While this is harmless in a short-lived script, it sets a poor example.
- **Fix:** Add `await client.close()` or use `async with` pattern.

#### M4. `_from_dict` catches bare `TypeError`
- **File:** `src/aqi_in_api/_client.py:66-69`
- **Issue:** The `try/except TypeError` is too broad — it could mask genuine bugs in the dataclass construction.
- **Fix:** Catch more specific exceptions or restructure to avoid bare except.

#### M5. Ruff config uses limited rule set
- **File:** `pyproject.toml`
- **Issue:** Only `E, F, I, N, W` selected. Missing many useful rules like `UP` (pyupgrade), `SIM` (simplify), `RET` (return), `ARG` (unused args), `PT` (pytest), `BLE` (blind exception).
- **Fix:** Expand rule selection.

#### M6. `get_slug_depth` uses type: ignore for return
- **File:** `src/aqi_in_api/_utils.py:34`
- **Issue:** The `# type: ignore[return-value]` is required because `int` arithmetic doesn't produce `Literal[1, 2, 3, 4]`.
- **Fix:** Could use `typing.cast(SlugType, depth)` instead of bare type ignore.

### 🟢 Low Priority

#### L1. Coverage gaps
- **Details:** `_client.py` at 70% — untested paths: `search()`, `get_last_12_hour_history()`, `get_last_7_days_history()`, `get_last_30_days_history()`, `get_rankings()`, and the `body.get("status") in ("failed",)` error branch.
- `_utils.py` at 89% — edge cases in `build_url`.
- `_exceptions.py` at 91% — `__str__` without body.
- **Fix:** Add integration-style tests with httpx_mock for the remaining methods.

#### L2. N815/N818 per-file-ignores without justification
- **File:** `pyproject.toml:36-37`
- **Issue:** N815 (mixed-case variable name), N818 (exception suffix). Suppressed without comment.
- **Fix:** Add inline `# noqa: N815` on specific fields with `# snake_case vs camelCase` comment, or document in pyproject.toml.

#### L3. No pre-commit config
- **Observation:** No `.pre-commit-config.yaml` for automated linting/formatting before commits.

---

## Architecture Assessment

```
src/aqi_in_api/
├── __init__.py       # Public API exports
├── _client.py        # Core client + request handling
├── _constants.py     # URLs, defaults
├── _exceptions.py    # Custom exception
├── _token.py         # JWT generation
├── _utils.py         # URL building, slug depth
└── models.py         # All data types (15 classes)
```

**Strengths:**
- Clean module separation (private `_*` modules, public `models.py`)
- Frozen dataclasses for immutability
- Type-safe with mypy strict mode
- Async-native with httpx
- Good test coverage (90%)

**Weaknesses:**
- Union type for `SlugType` (Literal[1,2,3,4]) is awkward with numeric operations
- `_from_dict`/`_convert_value` data mapping is verbose — a Pydantic-like approach would reduce complexity but add dependency
- Models module has 15 classes in one file — could eventually be split by domain
- No async context manager support (`async with AQIClient() as c:`)

---

## File-by-File Review

### `src/aqi_in_api/__init__.py` ✅
Clean public API surface. Exports `AQIClient`, `ClientConfig`, `create_aqi_client`, `AQIException`.

### `src/aqi_in_api/_client.py` ⚠️
Well-structured. Issues:
- No httpx timeout (H3)
- Bare `TypeError` in `_convert_value` (M4)
- Several `# type: ignore` annotations that could be cleaned up
- No `__all__`

### `src/aqi_in_api/models.py` ⚠️
Comprehensive type definitions. Issues:
- Missing `__all__` (M1)
- 15 classes in one file — nearing the split point
- `SlugType = Literal[1, 2, 3, 4]` is elegant but creates friction with `get_slug_depth()`

### `src/aqi_in_api/_token.py` ⚠️
Simple JWT generation. Issues:
- Hardcoded secret (H2) — intentional but needs suppression
- No `__all__`

### `src/aqi_in_api/_utils.py` ⚠️
Clean utility functions. Issues:
- `# type: ignore` on `get_slug_depth` return (M6)
- No `__all__`
- Minor: 89% coverage

### `src/aqi_in_api/_exceptions.py` ✅
Clean exception class. 91% coverage.

### `src/aqi_in_api/_constants.py` ✅
Simple constants. No issues.

### `tests/*` ⚠️
Good test coverage and patterns. Issues:
- PyJWT `InsecureKeyLengthWarning` in test output (H2)
- Missing tests for several API methods (L1)
- S101/assert warnings from ruff extended rules

### CI/CD ✅
Solid GitHub Actions setup. Likely pre-existing TypeScript porting.

---

## Recommendations Summary

### Must Fix (before shipping)
1. Add `py.typed` marker
2. Set httpx timeout
3. Add dev dependencies to pyproject.toml

### Should Fix
4. Add `__all__` to `models.py`
5. Update `example.py` to close client
6. Suppress JWT warnings in tests
7. Update dependabot config

### Nice to Have
8. Expand ruff rules
9. Add remaining API method tests
10. Add async context manager support for `AQIClient`
