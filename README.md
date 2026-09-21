# GitHub Challenge

<img src="https://octodex.github.com/images/Professortocat_v2.png" align="right" height="200px" />

Hey there!

Your challenge is ready.
Follow the instructions provided for this challenge and complete the required tasks in this repository.

Make sure your work is committed and pushed to your repository before submission.

Good luck!

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

Running `PYTHONPATH=src python3 src/aiops_pipeline.py` processed all 10 records, detected 2 anomalies, and consumed 2 events. The events at `2026-09-20T10:05:00` and `2026-09-20T10:06:00` travelled through the detector, producer, topic, and consumer and were present in the downstream pipeline result with their detection reasons.

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
PYTHONPATH=src python3 src/aiops_pipeline.py
```
The corrected execution processes 10 records, detects 2 anomalies, consumes 2 events, and prints the timestamp and reasons for each event. The full automated verification passes with:
```bash
python3 -m pytest -q
```
Result: `12 passed`.

## Task 6: Execute the End-to-End Pipeline

The corrected workflow was executed from the supplied operational data using:

```bash
PYTHONPATH=src python3 src/aiops_pipeline.py
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
