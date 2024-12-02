from datetime import datetime
from typing import NamedTuple
from google.cloud import aiplatform
from kfp import dsl
from kfp import compiler
from day_1.components import file_generator, file_updater, gather_metrics

GCP_PROJECT = "dev-sams-ds-train"
SERVICE_ACCOUNT = "svc-ds-train@dev-sams-ds-train.iam.gserviceaccount.com"
NETWORK = "projects/12856960411/global/networks/vpcnet-private-svc-access-usc1"
PIPELINE_ROOT = "gs://mlops-summit"

outputs = NamedTuple("outputs", artifact=dsl.Artifact, metrics=dsl.Metrics)


@dsl.pipeline(
    name="hello world pipeline",
    pipeline_root="gs://mlops-summit",
)
def pipeline() -> outputs:

    file_generator_task = (
        file_generator()
        .set_display_name("File Generator")
        .set_cpu_limit("2")
        .set_memory_limit("2G")
    )

    file_updater_task = (
        file_updater(artifact=file_generator_task.output)
        .set_display_name("File Updater")
        .set_cpu_limit("2")
        .set_memory_limit("2G")
    )

    gather_metrics_task = (
        gather_metrics(artifact=file_updater_task.output)
        .set_display_name("Gather Metrics")
        .set_cpu_limit("2")
        .set_memory_limit("2G")
    )

    return outputs(
        artifact=file_updater_task.output, metrics=gather_metrics_task.output
    )


if __name__ == "__main__":

    TMP_PIPELINE_YAML = "/tmp/hello-world-pipeline.yaml"

    compiler.Compiler().compile(
        pipeline_func=pipeline,
        package_path=TMP_PIPELINE_YAML,
    )

    pipeline_job = aiplatform.PipelineJob(
        display_name="hello-world-pipeline-" + datetime.now().strftime("%Y%m%d%H%M%S"),
        project=GCP_PROJECT,
        template_path=TMP_PIPELINE_YAML,
        enable_caching=False,
    )

    pipeline_job.submit(
        service_account=SERVICE_ACCOUNT,
        network=NETWORK,
    )
