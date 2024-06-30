import pandas as pd

## VIASH START
#Values are not hard-coded
par = {
  'input': 'filtered.csv',
  'output': 'report.pdf'
}
## VIASH END

#Read input file
df = pd.read_csv(par['input'])
# Convert time to datetime
df['time'] = pd.to_datetime(df['time_start'])
# Filter entries from the specified year
df_filtered_year = df[df['time'].dt.year == par['year']]
# Calculate total hours per project
project_hours = df_filtered_year.groupby('project')['duration'].sum().reset_index()
# Filter projects with total hours above the threshold
projects_above_threshold = project_hours[project_hours['duration'] >= par['min_duration_per_project']]
# Filter the original dataframe to keep only the projects above the threshold
df_filtered = df_filtered_year[df_filtered_year['project'].isin(projects_above_threshold['project'])]
# Save the filtered dataframe to a new CSV file
df_filtered.iloc[:,:-1].to_csv(par['output'], index=False)