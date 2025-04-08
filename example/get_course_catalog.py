import sys
import os
import json

# Add the parent directory to the path so we can import the src module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.course_catalog import extract_coursera_courses, convert_to_csv

def main():
    """Example script demonstrating how to extract courses from the Coursera catalog"""
    print("Testing course extraction...")
    
    # Default to 10 courses, but allow command line override
    limit = 10
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            print(f"Invalid limit: {sys.argv[1]}. Using default limit of 10.")
    
    print(f"Extracting up to {limit} courses...")
    courses = extract_coursera_courses(limit=limit)

    if courses:
        print(f"\nSuccessfully extracted {len(courses)} courses")
        print("\nSample of first course:")
        print(json.dumps(courses[0], indent=2))

        # Convert to CSV
        csv_path = convert_to_csv(courses)
        print(f"\nSaved to CSV: {csv_path}")
    else:
        print("Failed to extract any courses")

if __name__ == "__main__":
    main()