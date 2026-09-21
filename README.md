# GitHub Challenge

<img src="https://octodex.github.com/images/Professortocat_v2.png" align="right" height="200px" />

Hey there!

Your challenge is ready.
Follow the instructions provided for this challenge and complete the required tasks in this repository.

Make sure your work is committed and pushed to your repository before submission.

Good luck!

## Objective

This assessment demonstrates a Python-based AIOps workflow that analyses payment-service operational data, identifies abnormal behavior, processes anomaly events, and produces a final AIOps result.

## Task 1: Set Up and Understand the Environment

The service being monitored is `payment-service`, which produces metrics and log information during payment processing. The operational problem is to identify unusual response time or resource usage and connect those findings to relevant timeout logs.

The major repository components are:

- `data/service_data.json`: synthetic operational records containing metrics, logs, timestamps, and service information.
- `src/anomaly_detector.py`: checks metrics and log levels and creates anomaly events.
- `src/event_producer.py`: publishes anomaly events.
- `src/event_topic.py`: stores events in the in-memory topic.
- `src/event_consumer.py`: receives events from the topic.
- `src/aiops_pipeline.py`: loads the data, runs detection, connects the event components, and prints the final AIOps output.
- `tests/`: validates detection, event streaming, the end-to-end workflow, and code coverage.

The demonstrated workflow is:

`Operational Data -> Anomaly Detection -> Event Generation -> Producer -> Topic -> Consumer -> AIOps Output`

## Task 2

It has 10 payment records 
1. Metric Filed 
`response_time_ms`: request response time in milliseconds.
`cpu_percent`: CPU utilization percentage.
`memory_percent`: memory utilization percentage.
2. Log information fields
`log_level`: log severity, such as `INFO` or `ERROR`.
`message`: text describing the event or result.
3. Timestamp usage
Each record has an ISO 8601-style `timestamp`.
4. Observations that appear normal
The records from 10:00 through 10:04 and from 10:07 through 10:09 appear normal. Response time remains between 120 ms and 150 ms, CPU remains between 42% and 50%, and memory remains between 51% and 57%. These records have `INFO` logs stating that the payment request was processed successfully.
5. Observations that appear unusual
The records at 10:05 and 10:06 appear unusual

## Task 3: Identify Anomalies

The existing `AnomalyDetector` was used with the operational data. It checks response time, CPU utilization, memory utilization, and warning or error log levels against fixed thresholds. Detected events are published and consumed through the existing in-memory event-streaming classes.

### Detection report

- Records processed: 10.
- Anomalies detected: 2.
- Events consumed: 2.
- Normal observations: the records at 10:00 through 10:04 and 10:07 through 10:09 were not flagged.

The anomaly at `2026-09-20T10:05:00` was flagged for high response time and an error log. Its response time was 610 ms, with 75% CPU and 70% memory utilization. The log message was `Payment service timeout`.

The anomaly at `2026-09-20T10:06:00` was flagged for high response time, high CPU utilization, high memory utilization, and an error log. Its response time was 640 ms, with 94% CPU and 91% memory utilization. The log message was `Database connection timeout`.

### Expected anomalies and false positives

Both expected unusual observations were detected. No normal observation was incorrectly flagged in this dataset. The error-log condition was updated to include the dataset's `ERROR` records, and the producer and consumer now use the same `anomaly-events` topic so the detected events are available in the consumed report.

### Limitation and possible improvement

The detector uses fixed thresholds and does not learn a service-specific baseline. A possible improvement would be to calculate rolling baselines and detect deviations relative to recent behavior, while retaining explicit checks for severe log levels.

## Task 4: Verify the AIOps Event Flow
The complete anomaly-event flow was verified:
1. Anomaly detector: examines each operational record and creates an event when a metric threshold or concerning log level is found.
2. Producer: receives the event from the detector and publishes it.
3. Topic: stores the published event in the in-memory anomaly-events topic.
4. Consumer: reads the event from the same topic.
5. Event/message: contains the timestamp, service, anomaly type, reasons, and original source record.
6. Downstream AIOps result: the consumed events are returned by run_pipeline() in events_consumed, where the report displays their timestamps and reasons.

### Execution result

Running `python3 -m src.aiops_pipeline` processed all 10 records, detected 2 anomalies, and consumed 2 events. The events at `2026-09-20T10:05:00` and `2026-09-20T10:06:00` travelled through the detector, producer, topic, and consumer and were present in the downstream pipeline result with their detection reasons.

## Task 5: Investigate and Correct the Workflow

>Issue 1: Error logs were not detected
Affected component: `AnomalyDetector` in `src/anomaly_detector.py`.
Cause: the log condition checked only for `WARNING`, while the operational data contains `ERROR` records at 10:05 and 10:06.
Correction: the detector now treats both `WARNING` and `ERROR` as concerning log levels.
Re-execution: the 10:05 and 10:06 records are flagged with `Error log detected`.
Verification: the anomaly tests assert that an `ERROR` record includes the error-log reason, and the pipeline output reports both anomalies.

>Issue 2: Published events were not reaching the consumer

Affected components: `EventProducer`, `EventTopic`, `EventConsumer`, and `run_pipeline()`.
Cause: the producer was connected to `service-events`, while the consumer was connected to a separate `anomaly-events` topic.
Correction: the pipeline now creates one `anomaly-events` topic and passes that same topic to both the producer and consumer.
Re-execution: the producer publishes the two detected anomaly events and the consumer receives both.
Verification: the pipeline reports `Anomalies detected: 2` and `Events consumed: 2`; the end-to-end test also confirms that the published event appears in the consumer output and downstream pipeline result.

>Final verification
Run the workflow with:
```bash
python3 -m src.aiops_pipeline
```
The corrected execution processes 10 records, detects 2 anomalies, consumes 2 events, and prints the timestamp and reasons for each event. The full automated verification passes with:
```bash
python3 -m pytest -q
```
Result: `12 passed`.

## Task 6: Execute the End-to-End Pipeline

The corrected workflow was executed from the supplied operational data using:

```bash
python3 -m src.aiops_pipeline
```

The execution verified the complete path:

`Operational Data -> Anomaly Detection -> Event -> Producer -> Topic -> Consumer -> AIOps`

The final result was:

```text
Records processed: 10
Anomalies detected: 2
Events consumed: 2
```

The two final anomaly events identified the operational issue at `2026-09-20T10:05:00` and `2026-09-20T10:06:00`. The output included the affected service, timestamp, anomaly type, and detection reasons. This verifies that operational data was processed, abnormal behavior was detected, events were generated and published, the consumer received them, and the downstream AIOps result successfully represented the payment-service timeout and database connection timeout.

The end-to-end test in `tests/test_aiops_pipeline.py` separately verifies event creation, producer publication, topic storage, consumer receipt, and presence in the downstream `events_consumed` result.

## Task 7: Update the README

1. AIOps scenario

This project simulates an AIOps workflow for a payment application service. Operational records are inspected, abnormal service behavior is detected, and anomaly events are sent through a lightweight in-memory event-streaming workflow.

2. Operational data

The file `data/service_data.json` contains 10 records for `payment-service`. Each record includes a timestamp, response time, CPU percentage, memory percentage, log level, and log message. The records cover one-minute intervals from `2026-09-20T10:00:00` to `2026-09-20T10:09:00`.

3. Logs and metrics observations

The metric fields are `response_time_ms`, `cpu_percent`, and `memory_percent`. The log fields are `log_level` and `message`. Records from 10:00 through 10:04 and 10:07 through 10:09 appear normal because they have low and stable metric values with successful `INFO` messages. Records at 10:05 and 10:06 are unusual because response time, CPU, and memory increase and the logs report timeout errors.

4. Anomaly-detection findings

The `AnomalyDetector` identified two anomalies. The 10:05 record was flagged for high response time and an error log. The 10:06 record was flagged for high response time, high CPU utilization, high memory utilization, and an error log. No normal record was incorrectly flagged in the supplied data.

5. Event-processing flow

The workflow is:

`Operational Data -> AnomalyDetector -> Event -> EventProducer -> anomaly-events Topic -> EventConsumer -> AIOps result`

The detector creates an anomaly event, the producer publishes it to the topic, the consumer reads it, and `run_pipeline()` returns the received events in `events_consumed`.

6. Final workflow execution

The final execution produced:

```text
Records processed: 10
Anomalies detected: 2
Events consumed: 2
```

The final output identified the payment-service timeout at 10:05 and the database connection timeout at 10:06, including the timestamp, anomaly type, and reasons.

7. Issues corrected

The detector originally checked only `WARNING`, so it missed the dataset's `ERROR` log records. It was corrected to detect both `WARNING` and `ERROR`. The producer and consumer originally used different topics, so consumed events were empty. They were corrected to share the same `anomaly-events` topic. The package imports were standardized so the workflow runs with the package command used in the reproduction steps.

8. Limitation and possible improvement

The detector uses fixed thresholds and does not learn a service-specific baseline. A possible improvement is to calculate rolling baselines and detect deviations from recent behavior while continuing to treat severe log levels as anomalies.

9. Steps to reproduce

From the repository root, run:

```bash
python3 -m pip install -r requirements.txt
python3 -m pip install pytest-cov coverage
python3 -m src.aiops_pipeline
PYTHONPATH=. python3 -m pytest --cov=src --cov-report=term-missing --cov-fail-under=90 -q
```

The pipeline command displays the detected anomaly events. The test command runs all tests and verifies at least 90 percent code coverage. The current result is 18 passing tests and 100 percent coverage.

## Task 8: Run the Provided Validation

The provided validation was run after completing the implementation.

1. Operational data processing: passed. The workflow processed 10 records from `data/service_data.json`.
2. Anomaly detection: passed. The detector identified the two unusual records at 10:05 and 10:06.
3. Anomaly event generation: passed. Both detected records produced anomaly events with timestamps, source data, and reasons.
4. Event pipeline: passed. The producer published both events to the shared `anomaly-events` topic.
5. Consumer processing: passed. The consumer received both published events.
6. Final AIOps workflow: passed. The final output reported 2 anomalies and 2 consumed events.

Run the final workflow:

```bash
python3 -m src.aiops_pipeline
```

Run the complete tests and coverage validation:

```bash
PYTHONPATH=. python3 -m pytest --cov=src --cov-report=term-missing --cov-fail-under=90 -q
```

Validation result:

```text
18 passed
Required test coverage of 100% reached
Total coverage: 100.00%
```

No validation failures remained before submission.

## Task 9: Commit and Push Changes

Pull request: [Complete AIOps workflow assessment](https://github.com/DebbieAUG/github-skills-challenge/pull/222)

The modified files were reviewed before submission. Only files related to the assessment were included:

- `README.md`
- `src/aiops_pipeline.py`
- `src/anomaly_detector.py`
- `src/event_consumer.py`
- `src/event_producer.py`
- `tests/calculations_test.py`
- `tests/test_aiops_pipeline.py`

The changes were committed with meaningful task-specific commit messages. The final README update can be committed with:

```bash
git add README.md
git commit -m "Document final validation and submission steps"
git push origin main
```

Confirm the submission after pushing:

```bash
git status
git log -1 --oneline
git ls-remote origin refs/heads/main
```

The latest commit hash shown by `git log` should match the `main` hash returned by `git ls-remote`.
