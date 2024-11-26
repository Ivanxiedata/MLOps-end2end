from kfp import dsl

@dsl.component(
    base_image="python:3.10-slim",
)
def gather_metrics(artifact: dsl.Artifact) -> dsl.Metrics:
    metrics = dsl.Metrics(uri=dsl.get_uri(suffix="metrics.output"))
    print(f"Artifact Path: {metrics.path}")
    print(f"Artifact URI: {metrics.uri}")

    metrics.log_metric('metric_1', 0.00089238929)
    metrics.log_metric('metric_2', 0.8923782378)
    metrics.log_metric('file_length', sum(1 for _ in open(artifact.path)))
    return metrics

