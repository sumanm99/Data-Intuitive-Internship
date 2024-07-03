nextflow.enable.dsl=2

process runDockerExecutable {
    // Define the input and output channels
    input:
    path input
    path output
    val year
    val minDuration

    output:
    path("${output}")

    // Use Docker container
    container 'example_python_with_setup'

    script:
    """
    bin/example_python_with_setup --input ${input} --output ${output}/filtered.csv --year ${year} --min_duration_per_project ${minDuration}
    """
}

workflow {
    // Get input parameters from the command line
    input = file(params.input)
    output = file(params.output)
    year = params.year
    minDuration = params.min_duration_per_project

    // Create output directory if it doesn't exist
    if (!output.exists()) {
        output.mkdirs()
    }

    // Run the Docker executable
    runDockerExecutable(input, output, year, minDuration)
}
