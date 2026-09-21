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
