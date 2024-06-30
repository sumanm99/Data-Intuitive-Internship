import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

## VIASH START
#Values are not hard-coded
par = {
  'input': '../output/filtered.csv',
  'output': '../output/report.pdf'
}
## VIASH END

## Fetch details of filtered_csv
filtered_csv = pd.read_csv(par['input'])
year = pd.to_datetime(filtered_csv['time_start']).dt.year.unique()[0]
people = filtered_csv['person'].nunique()
projects = filtered_csv['project'].nunique()
#Times per project and person
person_project = filtered_csv.groupby(['project', 'person'])['duration'].sum().reset_index()
person_project.columns = ['Project', 'Person', 'Time (h)']
#Total hours
total_hours = person_project['Time (h)'].sum()
project_hours = person_project.groupby('Project')['Time (h)'].sum().reset_index()
project_hours.loc[len(project_hours.index)] = ['Total', total_hours]

## Create a stacked-bar graph
matplotlib.use('Agg') #To prevent matplotlib from not responding
# Convert time to datetime and remove timezone information if any
filtered_csv['Date'] = pd.to_datetime(filtered_csv['time_start']).dt.tz_localize(None)
# Extract the year-month from the date
filtered_csv['YearMonth'] = filtered_csv['Date'].dt.to_period('M')
person_hours = filtered_csv.groupby(['YearMonth', 'person'])['duration'].sum().unstack().fillna(0)

fig, ax = plt.subplots(figsize=(10, 6))
# Plot each person's hours as a stacked bar
person_hours.plot(kind='bar', stacked=True, ax=ax)
ax.set_xlabel('Month')
ax.set_ylabel('Time (hours)')
ax.set_title('Figure:', loc='left')
ax.set_xticklabels(person_hours.index.astype(str), rotation = 0)
ax.legend(title='Person', bbox_to_anchor=(0.5, -0.2), loc='upper center', ncol=len(person_hours.columns))
plt.tight_layout()
plt.show()

# Save plot to a BytesIO object
img = BytesIO()
plt.savefig(img, format='png')
img.seek(0)
plt.close()

## Create a PDF report
pdf = BytesIO()
doc = SimpleDocTemplate(pdf, pagesize=letter)
styles = getSampleStyleSheet()
elements = []

# Add text
title = Paragraph(f"Project report anno {year}", styles['Title'])
elements.append(title)
elements.append(Spacer(1, 12)) # Add spacer
line = Paragraph(f"This year, {people} people worked on {projects} different projects.", styles['BodyText'])
elements.append(line)
elements.append(Spacer(1, 12)) # Add spacer
line = Paragraph("Times per project and person (rounded down):", styles['BodyText'])
elements.append(line)
elements.append(Spacer(1, 12)) # Add spacer

# Add table
#Table 1
table_data = [person_project.columns.tolist()] + person_project.values.tolist() # Convert dataFrame to a list of lists
num_columns = len(table_data[0])
table = Table(table_data, colWidths=[doc.width / num_columns] * num_columns) #table spans the entire width of the page
table.setStyle(TableStyle([
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
]))
elements.append(table)
elements.append(Spacer(1, 12)) # Add spacer

line = Paragraph(f"In total, {total_hours} hours was worked across all projects. Times per project (rounded down):", styles['BodyText'])
elements.append(line)
elements.append(Spacer(1, 12)) # Add spacer

#Table 2
table_data = [project_hours.columns.tolist()] + project_hours.values.tolist() # Convert dataFrame to a list of lists
table = Table(table_data)
table.setStyle(TableStyle([
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
]))
table.hAlign = 'RIGHT' #table right-align
elements.append(table)
elements.append(Spacer(1, 12)) # Add spacer

# Add graph
elements.append(Image(img, width=doc.width, height=300))

## Build PDF
doc.build(elements)
pdf.seek(0)

## Save the PDF to a file
with open(par['output'], "wb") as f:
    f.write(pdf.getbuffer())