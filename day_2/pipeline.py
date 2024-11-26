from datetime import datetime
from google.cloud import aiplatform
from kfp import dsl
from kfp import compiler
from day_2.pipeline.components.features import create_training_data, fetch_iris_features

# Replace these values to the appropriate gcp project and service account you have access to
GCP_PROJECT = 'dev-sams-ds-train'
SERVICE_ACCOUNT = 'svc-ds-train@dev-sams-ds-train.iam.gserviceaccount.com'
NETWORK = 'projects/12856960411/global/networks/vpcnet-private-svc-access-usc1'

@dsl.component(
    base_image="python:3.10-slim",
)
def hello_world():
    print("HELLO WORLD")


@dsl.pipeline(name='hello world pipeline')
def pipeline():

    fetch_iris_features_task = (
        fetch_iris_features(
            project_id='',
            feature_view=''
        )
        .set_display_name("Fetch Features")
        .set_cpu_limit('2')
        .set_memory_limit('2G')
    )

    create_training_data_task = (
        create_training_data(
            features_input=fetch_iris_features_task.output,
            test_ratio=0.25
        )
        .set_display_name("Fetch Features")
        .set_cpu_limit('2')
        .set_memory_limit('2G')
    )

if __name__ == "__main__":

    TMP_PIPELINE_JSON = '/tmp/persona-pipeline.json'

    # Compile the pipeline into a json DAG specification
    compiler.Compiler().compile(
        pipeline_func=pipeline,
        package_path=TMP_PIPELINE_JSON,
    )

    pipeline_job = aiplatform.PipelineJob(
        display_name='hello-world-pipeline-'+datetime.now().strftime("%Y%m%d%H%M%S"),
        project=GCP_PROJECT,
        template_path=TMP_PIPELINE_JSON,
        enable_caching=True,
    )

    pipeline_job.submit(
        service_account=SERVICE_ACCOUNT, 
        network=NETWORK,

    )


