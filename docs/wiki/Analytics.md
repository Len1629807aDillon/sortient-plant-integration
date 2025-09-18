# Analytics and Monitoring

This section outlines how to leverage the analytics toolkit within Sortient Plant Integration.

## Metrics Catalogue

- **Detection Accuracy** – Confusion matrix, macro accuracy, weighted accuracy
- **Throughput** – Items per hour across sliding windows and trend analysis
- **Recovery Rate** – Material-specific recovery performance
- **OEE** – Availability × Performance × Quality
- **Predictive Maintenance** – Failure probability and recommended actions per component

## Usage Patterns

1. Use `compute_confusion_matrix` and `compute_accuracy_breakdown` to evaluate model performance.
2. Aggregate throughput with `ThroughputWindow.throughput_per_hour()` and
   `throughput_trend(window)` to track variability across shifts.
3. Combine `compute_oee_breakdown` with operations data for executive dashboards.
4. Surface `PredictiveMaintenanceInsight` records in maintenance management systems and prioritise by
   failure probability.
5. Apply `moving_average` when smoothing sensor-derived KPIs prior to alerting.

## Integrations

- Export metrics to JSON for ingestion into data warehouses or data lakes.
- Wire throughput, trend, and OEE metrics to Prometheus exporters or Grafana dashboards.
- Align predictive maintenance insights with CMMS to automate work orders and spare-part logistics.

