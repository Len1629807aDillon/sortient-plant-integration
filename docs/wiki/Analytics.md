# Analytics and Monitoring

This section outlines how to leverage the analytics toolkit within Sortient Plant Integration.

## Metrics Catalogue

- **Detection Accuracy** – Confusion matrix, macro accuracy, weighted accuracy
- **Throughput** – Items per hour across sliding windows
- **Recovery Rate** – Material-specific recovery performance
- **OEE** – Availability × Performance × Quality
- **Predictive Maintenance** – Failure probability and recommended actions per component

## Usage Patterns

1. Use `compute_confusion_matrix` and `compute_accuracy_breakdown` to evaluate model performance.
2. Aggregate throughput with `ThroughputWindow.throughput_per_hour()` to track variability across
   shifts.
3. Combine `compute_oee` with operations data for executive dashboards.
4. Surface `PredictiveMaintenanceInsight` records in maintenance management systems.

## Integrations

- Export metrics to JSON for ingestion into data warehouses.
- Wire throughput and recovery metrics to Prometheus exporters.
- Align predictive maintenance insights with CMMS to automate work orders.

