from datetime import datetime
from typing import NamedTuple
from google.cloud import aiplatform
from kfp import dsl
from kfp import compiler
from day_1.components import file_generator, file_updater, gather_metrics
from day_1.components.config import (
    GCP_PROJECT,
    SERVICE_ACCOUNT,
    NETWORK,
    PIPELINE_NAME,
    PIPELINE_ROOT,
    CPU_LIMIT,
    MEMORY_LIMIT)

outputs = NamedTuple("outputs", artifact=dsl.Artifact, metrics=dsl.Metrics)


@dsl.pipeline(
    name=PIPELINE_NAME,
    pipeline_root=PIPELINE_ROOT,
)
def pipeline() -> outputs:
    file_generator_task = (
        file_generator()
        .set_display_name("File Generator")
        .set_cpu_limit(CPU_LIMIT)  # the CPU MAX limit to 96 CPUs
        .set_memory_limit(MEMORY_LIMIT)  # the memory MAX limit to 624 Gigabytes
        # .set_accelerator_type('NVIDIA_A100_80GB')
        # .set_accelerator_limit(2)
        # .add_node_selector_constraint('GPU')
    )

    file_updater_task = (
        file_updater(artifact=file_generator_task.output)
        .set_display_name("File Updater")
        .set_cpu_limit(CPU_LIMIT)  # the CPU MAX limit to 96 CPUs
        .set_memory_limit(MEMORY_LIMIT)  # the memory MAX limit to 624 Gigabytes
        # .set_accelerator_type('NVIDIA_A100_80GB')
        # .set_accelerator_limit(2)
        # .add_node_selector_constraint('GPU')
    )

    gather_metrics_task = (
        gather_metrics(artifact=file_updater_task.output)
        .set_display_name("Gather Metrics")
        .set_cpu_limit(CPU_LIMIT)  # the CPU MAX limit to 96 CPUs
        .set_memory_limit(MEMORY_LIMIT)  # the memory MAX limit to 624 Gigabytes
        # .set_accelerator_type('NVIDIA_A100_80GB')
        # .set_accelerator_limit(2)
        # .add_node_selector_constraint('GPU')
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
