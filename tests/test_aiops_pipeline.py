from pathlib import Path

from src.anomaly_detector import AnomalyDetector
from src.aiops_pipeline import identify_metric_fields, run_pipeline
from src.event_consumer import EventConsumer
from src.event_producer import EventProducer
from src.event_topic import EventTopic


def test_normal_record_is_not_anomaly():
    detector = AnomalyDetector()

    record = {
        "timestamp": "2026-09-20T10:00:00",
        "service": "payment-service",
        "response_time_ms": 120,
        "cpu_percent": 42,
        "memory_percent": 51,
        "log_level": "INFO",
        "message": "Payment request processed successfully"
    }

    assert detector.detect(record) is None


def test_identify_metric_fields_from_records():
    records = [
        {
            "timestamp": "2026-09-20T10:00:00",
            "service": "payment-service",
            "response_time_ms": 120,
            "cpu_percent": 42,
            "memory_percent": 51,
            "log_level": "INFO",
            "message": "Payment request processed successfully"
        }
    ]

    assert identify_metric_fields(records) == [
        "cpu_percent",
        "memory_percent",
        "response_time_ms"
    ]


def test_pipeline_reports_metric_fields():
    result = run_pipeline(str(Path("data/service_data.json")))

    assert result["metric_fields"] == [
        "cpu_percent",
        "memory_percent",
        "response_time_ms"
    ]


def test_anomalous_record_is_detected():
    detector = AnomalyDetector()

    record = {
        "timestamp": "2026-09-20T10:05:00",
        "service": "payment-service",
        "response_time_ms": 610,
        "cpu_percent": 75,
        "memory_percent": 70,
        "log_level": "ERROR",
        "message": "Payment service timeout"
    }

    event = detector.detect(record)

    assert event is not None
    assert event["type"] == "ANOMALY"
    assert "High response time" in event["reasons"]
    assert "Error log detected" in event["reasons"]


def test_pipeline_consumes_detected_anomalies():
    result = run_pipeline(str(Path("data/service_data.json")))

    assert result["records_processed"] == 10
    assert len(result["anomalies_detected"]) == 2
    assert len(result["events_consumed"]) == 2
    assert result["events_consumed"] == result["anomalies_detected"]
    assert all(event["reasons"] for event in result["events_consumed"])


def test_anomaly_event_travels_through_complete_flow():
    record = {
        "timestamp": "2026-09-20T10:06:00",
        "service": "payment-service",
        "response_time_ms": 640,
        "cpu_percent": 94,
        "memory_percent": 91,
        "log_level": "ERROR",
        "message": "Database connection timeout"
    }
    detector = AnomalyDetector()
    topic = EventTopic("anomaly-events")
    producer = EventProducer(topic)
    consumer = EventConsumer(topic)

    event = detector.detect(record)

    assert event is not None
    assert producer.publish(event) is True
    assert topic.get_messages() == [event]

    received_events = consumer.consume()

    assert received_events == [event]
    assert received_events[0]["timestamp"] == record["timestamp"]
    assert received_events[0]["reasons"]

    pipeline_result = run_pipeline(str(Path("data/service_data.json")))
    downstream_events = pipeline_result["events_consumed"]

    assert any(
        downstream_event["timestamp"] == record["timestamp"]
        for downstream_event in downstream_events
    )


def test_producer_publishes_event():
    topic = EventTopic("anomaly-events")
    producer = EventProducer(topic)

    event = {
        "type": "ANOMALY",
        "service": "payment-service"
    }

    assert producer.publish(event)
    assert len(topic.get_messages()) == 1


def test_consumer_receives_event():
    topic = EventTopic("anomaly-events")
    producer = EventProducer(topic)
    consumer = EventConsumer(topic)

    event = {
        "type": "ANOMALY",
        "service": "payment-service"
    }

    producer.publish(event)

    messages = consumer.consume()

    assert len(messages) == 1