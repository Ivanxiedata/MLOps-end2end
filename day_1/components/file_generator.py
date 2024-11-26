from kfp import dsl

@dsl.component(
    base_image="python:3.10-slim",
)
def file_generator() -> dsl.Artifact:
    artifact = dsl.Artifact(uri=dsl.get_uri(suffix="generated_artifact.txt"))
    print(f"Artifact Path: {artifact.path}")
    print(f"Artifact URI: {artifact.uri}")

    with open(artifact.path, "w") as text_file:
        text_file.write("Created by file_generator!\n")
    
    return artifact

