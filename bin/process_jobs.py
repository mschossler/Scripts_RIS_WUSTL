import os
import csv
import re

# Get the home directory
home_directory = os.path.expanduser("~")

# Define the file paths
current_jobs_file = os.path.join(home_directory, 'current_jobs.csv')
jobs_submitted_file = os.path.join(home_directory, 'jobs_submitted.csv')
output_file = os.path.join(home_directory, 'jobs.csv')
output_file_txt = os.path.join(home_directory, 'jobs.txt')

# Read the CSV files into lists of dictionaries
with open(current_jobs_file, mode='r') as f:
    current_jobs_reader = csv.DictReader(f)
    current_jobs = list(current_jobs_reader)

with open(jobs_submitted_file, mode='r') as f:
    jobs_submitted_reader = csv.DictReader(f)
    jobs_submitted = list(jobs_submitted_reader)

# Create a mapping from JobID to job submission details
jobs_submitted_map = {job['JobID']: job for job in jobs_submitted}

# Merge the data
merged_jobs = []
for job in current_jobs:
    job_id = job['jobid']
    merged_job = job.copy()
    if job_id in jobs_submitted_map:
        for key, value in jobs_submitted_map[job_id].items():
            merged_job[key] = value
        merged_jobs.append(merged_job)
    else:
        print(f"Job ID {job_id} not found in jobs_submitted")

# Function to extract number from exec_host
def extract_number(exec_host):
    match = re.search(r'exec-(\d+)\.ris', exec_host)
    # print('here')
    return match.group(1) if match else None

# Move 'stat' and 'exec_host' to the end of each job dictionary
# Update 'exec_host' and create a new 'link' column
for job in merged_jobs:
    if 'exec_host' in job and 'Port' in job and 'Token' in job:
        number_exec_host = extract_number(job['exec_host'])
        if number_exec_host:
            job['link'] = f"http://compute1-exec-{number_exec_host}.ris.wustl.edu:{job['Port']}/lab?token={job['Token']}"
        else:
            job['link'] = None
    if 'stat' in job:
        job['stat'] = job.pop('stat')
    if 'exec_host' in job:
        job['exec_host'] = job.pop('exec_host')

# Define the fields to write, ensuring 'stat' and 'exec_host' are last
if merged_jobs:
    fields = list(merged_jobs[0].keys())
    fields = [field for field in fields if field not in {'queue', 'job_name'}]
    if 'stat' in fields:
        fields.append(fields.pop(fields.index('stat')))
    if 'exec_host' in fields:
        fields.append(fields.pop(fields.index('exec_host')))

    # Write the merged data to the output CSV file
    with open(output_file, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for job in merged_jobs:
            job = {key: job[key] for key in fields}
            writer.writerow(job)

def csv_to_human_readable_txt(csv_file_path, txt_file_path):
    # Read the CSV file and determine the maximum width of each column
    with open(csv_file_path, mode='r', newline='') as csv_file:
        csv_reader = list(csv.reader(csv_file))
        col_widths = [max(len(str(cell)) for cell in col) for col in zip(*csv_reader)]

    # Write to the text file with aligned columns
    with open(txt_file_path, mode='w') as txt_file:
        for row in csv_reader:
            aligned_row = [str(cell).ljust(width) for cell, width in zip(row, col_widths)]
            txt_file.write(' | '.join(aligned_row) + '\n')

csv_to_human_readable_txt(output_file, output_file_txt)