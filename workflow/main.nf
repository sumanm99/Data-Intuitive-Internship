nextflow.enable.dsl=2

params.base = "$baseDir"

process filterTimesheets {
    // Define the input and output channels
    input:
    path input
    path outputDir
    val year
    val minDuration

    output:
    path("${outputDir}/filtered.csv")

    script:
    """
    echo "${params.base}"
    mnt/d/Data_Intuitive_Internship/GitHub/bin/example_python_with_setup --input ${input} --output ${outputDir}/filtered.csv --year ${year} --min_duration_per_project ${minDuration}
    """
}

process generateReport {
    input:
    path filteredFile

    output:
    path("${filteredFile.getParent()}/report.pdf")

    script:
    """
    mnt/d/Data_Intuitive_Internship/GitHub/bin/example2_python_with_setup --input ${filteredFile} --output ${filteredFile.getParent()}/report.pdf
    """
}

workflow {
    // Get input parameters from the command line
    input = file(params.input)
    outputDir = file(params.outputDir)
    year = params.year
    minDuration = params.minDuration

    // Run the Docker executable to filter data
    filteredFile = filterTimesheets(input: input, outputDir: outputDir, year: year, minDuration: minDuration)

    // Generate the report using the filtered data
    generateReport(filteredFile)
}