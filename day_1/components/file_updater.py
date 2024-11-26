from kfp import dsl

@dsl.component(
    base_image="python:3.10-slim",
)
def file_updater(artifact: dsl.Artifact) -> dsl.Artifact:
    updated_artifact = dsl.Artifact(uri=dsl.get_uri(suffix="updated_artifact.txt"))
    print(f"Input Artifact Path: {artifact.path}")
    print(f"Input Artifact URI: {artifact.uri}")
    print(f"Output Artifact Path: {updated_artifact.path}")
    print(f"Output Artifact URI: {updated_artifact.uri}")

    with open(artifact.path, "r") as file:
        input_artifact_content = file.read()
    
    with open(updated_artifact.path, "w") as file:
        file.write(input_artifact_content+"Updated by file_updater!\n")
    return updated_artifact

