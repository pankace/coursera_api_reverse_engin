# Coursera API Client

A Python client for retrieving course information from Coursera's API. This library provides functionality to:

- Fetch detailed information about specific courses using their slug
- Extract course catalog data with filtering options
- Export course data to CSV
- Upload data to Google Cloud Storage (optional)

## Installation

```bash
pip install -r requirements.txt
```

## Usage Examples

### Get Course Details

```python
from src.course_details import get_course_details, extract_basic_info

# Get details for a specific course
response = get_course_details("machine-learning")
if response:
    course_info = extract_basic_info(response)
```
### Verify Course Ammount

```python
url = "https://api.coursera.org/api/courses.v1?start=0&limit=2150&includes=instructorIds,partnerIds,specializations,s12nlds,v1Details,v2Details&fields=instructorIds,partnerIds,specializations,s12nlds,description"
data = requests.get(url).json()
print(len(data['elements']))
```

### Extract Course Catalog

```python
from src.course_catalog import extract_coursera_courses, convert_to_csv

# Extract courses from catalog
courses = extract_coursera_courses(limit=20)
if courses:
    csv_path = convert_to_csv(courses)
    print(f"Data saved to {csv_path}")
```

### Upload to Google Cloud Storage

```python
from src.storage import upload_to_gcs

# Upload a file to GCS
result = upload_to_gcs(
    local_file_path="coursera_courses.csv",
    bucket_name="your-bucket-name",
    make_public=True
)
if result:
    print(f"File uploaded to {result['path']}")
```