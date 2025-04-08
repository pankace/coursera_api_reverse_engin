import sys
import os

# Add the parent directory to the path so we can import the src module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.course_catalog import extract_coursera_courses, convert_to_csv
from src.storage import upload_to_gcs, ensure_bucket_exists

def main():
    """
    Example script demonstrating how to extract courses and upload to GCS
    """
    # Check for bucket name as command line argument
    if len(sys.argv) < 2:
        print("Usage: python upload_to_gcs.py <bucket-name> [limit]")
        return
    
    # Get bucket name from command line
    bucket_name = sys.argv[1]
    
    # Default to 10 courses, but allow command line override for limit
    limit = 10
    if len(sys.argv) > 2:
        try:
            limit = int(sys.argv[2])
        except ValueError:
            print(f"Invalid limit: {sys.argv[2]}. Using default limit of 10.")
    
    print("Starting course data extraction...")

    # Extract courses
    print(f"Extracting up to {limit} courses...")
    courses = extract_coursera_courses(limit=limit)

    if not courses:
        print("Failed to extract courses. Exiting.")
        return

    print(f"Successfully extracted {len(courses)} courses")

    # Convert to CSV
    print("Converting courses to CSV...")
    csv_path = convert_to_csv(courses)

    if not csv_path:
        print("Failed to create CSV file. Exiting.")
        return

    # Upload to Google Cloud Storage
    print(f"Uploading {csv_path} to Google Cloud Storage bucket {bucket_name}...")
    result = upload_to_gcs(
        local_file_path=csv_path,
        bucket_name=bucket_name,
        make_public=True,
        metadata={
            "source": "coursera_api",
            "extraction_date": os.path.basename(csv_path).split("_")[1],
            "record_count": str(len(courses))
        }
    )

    if result:
        print("File uploaded successfully!")
        print(f"GCS Path: {result['path']}")
        if result.get('url'):
            print(f"Public URL: {result['url']}")
    else:
        print("Failed to upload file to GCS")

if __name__ == "__main__":
    main()