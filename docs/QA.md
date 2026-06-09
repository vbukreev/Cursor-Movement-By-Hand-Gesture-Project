# Quality Assurance & Testing Strategy

**Project:** AeroPoint – Gesture-Driven Cursor Control System
**Course:** Capstone II
**Team:**

| Name | Role | Email |
|---|---|---|
| Victoria Bukreev | Project Lead & System Integration | vbukreev@myseneca.ca |
| Kunal | Backend & Gesture Recognition Developer | k63@myseneca.ca |
| Aditi | Testing & Integration Developer | aditi2@myseneca.ca |
| Preksha Sharda | UI/UX & Documentation Developer | psharda3@myseneca.ca |

**Repository:** https://github.com/vbukreev/Cursor-Movement-By-Hand-Gesture-Project
**Document Version:** 1.0
**Last Updated:** 2026-05-31

---

## Table of Contents

1. [Testing Goals](#1-testing-goals)
2. [Planned Types of Testing](#2-planned-types-of-testing)
   - [Unit Testing](#21-unit-testing)
   - [Integration Testing](#22-integration-testing)
   - [End-to-End Testing](#23-end-to-end-e2e-testing)
   - [Manual Testing](#24-manual-testing)
   - [Performance Testing](#25-performance--load-testing)
   - [Security Testing](#26-security-testing)
3. [Sprint-Based Testing Schedule](#3-sprint-based-testing-schedule)
4. [Pull Request Quality Rules](#4-pull-request-quality-rules)
5. [Team Testing Responsibilities](#5-team-testing-responsibilities)

---

## 1. Testing Goals

AeroPoint is a real-time, computer vision application that translates live webcam hand gestures into operating system cursor actions — movement, clicking, and scrolling. Unlike a typical web application, AeroPoint runs a continuous processing loop interfacing directly with hardware (webcam) and the host OS (cursor control via PyAutoGUI). This means failures are often silent, immediate, and visible to the user.

### Why Testing Is Important for AeroPoint

Testing is critical because:

- The system runs a real-time loop processing 20–30 frames per second. Any unhandled exception silently freezes the application with no user feedback.
- Cursor actions interact directly with the host operating system. An incorrect click or uncontrolled cursor movement cannot be undone and directly disrupts the user.
- MediaPipe landmark detection is sensitive to environmental factors like lighting, hand angle, and distance from camera. The gesture logic must handle degraded or missing input gracefully.
- The calibration module maps the user's physical hand range to screen coordinates. A bug here causes all subsequent cursor movement to be systematically wrong.
- The PySide6 UI runs on a separate thread. Poor thread management between the UI and the gesture processing loop will cause dropped frames or frozen interfaces.

### Risks the Team Is Working to Reduce

| Risk | Likelihood | Impact |
|---|---|---|
| MediaPipe returns `None` landmarks unexpectedly | High | App crash |
| Calibration produces out-of-bounds screen coordinates | Medium | Cursor teleportation / OS exception |
| Pinch gesture misfires and registers unintended clicks | High | Poor user experience, lost trust |
| Camera stream fails with no graceful fallback | Medium | Silent application freeze |
| UI thread blocks gesture processing loop | Medium | Dropped frames, laggy tracking |
| Dependency vulnerability in OpenCV or MediaPipe | Low | Security exposure |

### Most Critical Failure Types

The most critical failures for AeroPoint are:

- **Application crashes** — any unhandled exception kills the gesture loop and leaves the user with no cursor control
- **False click detection** — the pinch gesture triggering unintended OS-level clicks is the single most disruptive user-facing failure
- **Calibration failure** — if the coordinate mapping is wrong, the cursor will never reach the edges of the screen, making the system unusable

---

## 2. Planned Types of Testing

### 2.1 Unit Testing

**Framework:** `pytest` with `pytest-mock` and `pytest-cov`

Unit tests verify individual functions and classes in complete isolation. Hardware dependencies (webcam frames, MediaPipe, PyAutoGUI, OS calls) are replaced with mocks so tests run in any environment including CI.

**Source files targeted:**

| Source File | What Will Be Unit Tested |
|---|---|
| `src/gestures.py` | Pinch detection threshold logic, scroll direction classification, finger-state array calculation |
| `src/calibrator.py` | Hand-to-screen coordinate mapping, boundary clamping, sensitivity scaling |
| `src/controller.py` | Movement delta calculation, click throttle/debounce, scroll direction sign |
| `src/hand_tracker.py` | Landmark extraction, confidence thresholding, `None` guard when no hand detected |
| `src/settings.py` | Default value loading, value validation, settings persistence logic |

**Minimum coverage goal:** 70% line coverage across `src/`, enforced in CI using `pytest-cov`.

**Example unit test scenarios:**

- `gestures.py`: pinch detection returns `True` when thumb-index distance is below configured threshold, `False` above
- `calibrator.py`: output coordinates are always clamped to `[0, screen_width]` and `[0, screen_height]` regardless of input
- `controller.py`: `move()` does not invoke `pyautogui.moveTo()` when the position delta falls within the deadzone
- `hand_tracker.py`: `extract_landmarks()` returns `None` without raising an exception when MediaPipe produces an empty result

**Running unit tests locally:**
```bash
pytest tests/unit/ --cov=src --cov-report=term-missing -v
```

---

### 2.2 Integration Testing

**Framework:** `pytest` with controlled fixture-based synthetic inputs

Integration tests verify that two or more modules work correctly when connected together. These tests do not use a live webcam or real OS cursor — inputs are synthetic numpy arrays and mocked PyAutoGUI calls.

**Integration pairs under test:**

| Modules Integrated | What Is Verified |
|---|---|
| `hand_tracker.py` + `gestures.py` | Landmark data flows from tracker to gesture classifier without loss or transformation errors |
| `gestures.py` + `controller.py` | Each recognized gesture type correctly triggers the corresponding cursor action |
| `calibrator.py` + `controller.py` | Calibrated coordinate range correctly constrains all movement commands to valid screen bounds |
| `app.py` + all modules | The main orchestration loop produces a non-error output for a synthetic sequence of frames |
| `settings.py` + `gestures.py` | User-configured sensitivity values correctly affect gesture thresholds at runtime |

**Integration test approach:**

Synthetic OpenCV frames are generated using `numpy` to represent known hand positions. These are passed through the real module code with only PyAutoGUI and OS-level calls mocked. This ensures the real logic is exercised without hardware.

---

### 2.3 End-to-End (E2E) Testing

**Approach:** Primarily manual, with one automated smoke test using a pre-recorded video

Full automated E2E testing is not feasible for AeroPoint because it requires a live webcam and real OS cursor interaction. The following complete user workflows will be manually verified by **Aditi** at the end of each sprint and recorded in `docs/manual-test-log.md`.

**E2E workflows to be tested:**

| # | Workflow | Expected Result |
|---|---|---|
| 1 | Application launch | App opens, camera preview appears, no console errors |
| 2 | Hand enters frame | Landmarks appear as overlay within 1 second |
| 3 | Calibration — four corners | User touches all four screen corners; cursor reaches each correctly |
| 4 | Open-palm cursor movement | Cursor follows hand smoothly with no visible jitter or lag |
| 5 | Pinch left-click | Exactly one click registered; no double-fire |
| 6 | Two-finger scroll | Browser or file list scrolls in the correct direction |
| 7 | Hand leaves frame | System enters idle state; no crash, cursor stops |
| 8 | Hand returns after idle | Tracking resumes without restarting the application |
| 9 | PySide6 settings panel | Panel opens, sensitivity changes take effect in real time |
| 10 | Extended session (10 min) | No memory growth or frame rate degradation observed |

**Automated smoke test:**
A pre-recorded `.mp4` of a hand performing basic gestures will be fed into OpenCV via `cv2.VideoCapture(path)` and passed through the real pipeline. The test asserts that the pipeline produces a non-empty gesture classification for each frame batch. This test lives in `tests/smoke/test_smoke.py` and runs in CI.

---

### 2.4 Manual Testing

Manual testing covers aspects of the system that cannot be meaningfully automated, including subjective usability and hardware variation.

**Usability testing:**
- A minimum of two external testers (peers unfamiliar with AeroPoint) will complete the calibration and gesture workflow while being observed by **Preksha Sharda**
- Testers will not receive instruction beyond what the UI provides — this validates the sufficiency of on-screen guidance
- Findings will be recorded in `docs/manual-test-log.md` including: calibration completion time, gesture failure count, confusion points, and suggested improvements

**Environmental variation:**
- Testing will be performed under three lighting conditions: dim room, bright overhead lighting, and a window behind the user (backlit)
- Testing will be performed with at least two camera resolutions (720p and 1080p)

**Visual / UI verification:**
- All PySide6 UI screens (splash, calibration, settings, main view) will be visually verified on a 1080p display
- Gesture overlay landmarks and on-screen indicators will be checked for correct positioning

**Session stability:**
- The application will be run continuously for at least 10 minutes and FPS will be observed at the start and end of the session

---

### 2.5 Performance / Load Testing

AeroPoint must maintain a smooth user experience while processing live video in a continuous loop.

**Frame rate target:** ≥ 20 FPS during active gesture tracking on a standard development laptop

**What will be measured:**

| Metric | Tool | Target |
|---|---|---|
| Frames per second (FPS) | Built-in FPS counter in `camera_stream.py` | ≥ 20 FPS |
| Per-frame processing time | `cProfile` on the gesture loop | < 50ms per frame |
| Memory usage over time | `tracemalloc` over a 10-minute session | No sustained growth |
| CPU utilization | OS task manager / `psutil` | < 80% on a single core |

**Performance test procedure:**
1. Launch AeroPoint on a clean system
2. Record FPS for 60 seconds with no hand present (baseline)
3. Record FPS for 60 seconds with hand tracked but no gesture
4. Record FPS for 60 seconds with continuous gesture input (rapid pinch + scroll)
5. Log all results to `docs/performance-report.md`

**Potential bottlenecks identified:**
- `hand_tracker.py` — MediaPipe inference runs on every frame and dominates per-frame cost
- `camera_stream.py` — frame buffer management under high frame rate
- `app.py` — coordination overhead between the camera thread and the gesture processing loop

---

### 2.6 Security Testing

Although AeroPoint does not handle user accounts or network communication, several security concerns are relevant to an application that accesses hardware and controls the OS cursor.

| Concern | How It Will Be Addressed |
|---|---|
| Webcam accessed without user awareness | Application must display a visible camera preview at all times; no background capture; tested on first launch |
| PyAutoGUI receives invalid screen coordinates | Unit tests confirm all coordinates are clamped before any call to `pyautogui`; values are never derived directly from raw landmark input |
| Dependency vulnerabilities (OpenCV, MediaPipe, PySide6) | `pip-audit` runs automatically in CI on every push and PR; flagged CVEs are reviewed and patched where a safe version is available |
| PySide6 settings panel — invalid user input | Settings values are validated and bounded before being applied to gesture thresholds; invalid input is rejected silently with the previous valid value retained |
| No data leaves the device | All frame processing is in-memory only; no webcam data is written to disk or transmitted over a network; verified by code review |

---

## 3. Sprint-Based Testing Schedule

Testing is integrated into the Capstone II sprint cycle rather than left to the end of the project. The following schedule outlines when each type of testing is planned.

| Sprint | Testing Activities | Owner |
|---|---|---|
| Sprint 1 | Set up `pytest` infrastructure and folder structure; write unit tests for `gestures.py` and `hand_tracker.py`; configure CI pipeline | Aditi, Kunal |
| Sprint 2 | Write unit tests for `calibrator.py`, `controller.py`, `settings.py`; write integration tests for tracker + gesture + controller pipeline; first manual E2E walkthrough | Aditi, all members |
| Sprint 3 | Automated smoke test with pre-recorded video; usability testing with 2 external testers; performance benchmark run; `pip-audit` review | Aditi, Preksha |
| Sprint 4 | Full E2E manual re-test of all 10 workflows; review and update `docs/manual-test-log.md`; final coverage report; address any CI failures before submission | All members |

---

## 4. Pull Request Quality Rules

The following rules apply to all Pull Requests targeting the `main` branch:

- All CI checks must pass before a PR can be merged — this includes linting, unit tests, and coverage threshold
- Every PR must be reviewed and approved by at least one other team member before merging
- Direct pushes to `main` are not permitted under any circumstances
- PRs must include a clear description of what changed, why, and any testing performed
- Any PR that adds new logic to `src/` must include corresponding unit tests; if tests are not included, written justification is required in the PR description
- The overall `pytest-cov` line coverage must not decrease below 70% as a result of the PR
- `flake8` and `pylint` must report zero errors; warnings are reviewed but do not block merging

---

## 5. Team Testing Responsibilities

| Team Member | Testing Responsibilities |
|---|---|
| **Aditi** | Owns the test suite; writes and maintains unit and integration tests; conducts E2E manual test sessions; maintains `docs/manual-test-log.md`; reviews CI failures |
| **Victoria Bukreev** | Reviews and approves test plans and CI configuration; signs off on QA before each milestone; monitors overall coverage report |
| **Kunal** | Writes unit tests for `gestures.py` and `hand_tracker.py`; reviews gesture logic test coverage; assists Aditi with integration test fixtures |
| **Preksha Sharda** | Conducts usability testing sessions and records findings; visually verifies PySide6 UI screens; updates `docs/manual-test-log.md` with UI feedback |
