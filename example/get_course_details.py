import sys
import json
import os

# Add the parent directory to the path so we can import the src module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.course_details import get_course_details, extract_basic_info

def main():
    """
    Example script demonstrating how to get details for specific courses
    """
    # Example course slugs to test
    test_courses = [
        "machine-learning",      # Andrew Ng's Machine Learning course
        "python",                # Python for Everybody
        "deep-learning-specialization"  # Deep Learning Specialization
    ]

    print("Coursera API Test - Course Details\n")

    for slug in test_courses:
        print(f"\nFetching details for course: {slug}")
        response = get_course_details(slug)

        if response:
            # Extract and display basic information
            course_info = extract_basic_info(response)
            
            if course_info:
                # Print formatted information
                print("\n---- COURSE DETAILS ----")
                print(f"Name: {course_info['name']}")
                print(f"Level: {course_info['level']}")
                print(f"Workload: {course_info['workload']}")
                print(f"Partners: {', '.join(course_info['partners'])}")
                print(f"Instructors: {', '.join(course_info['instructors'])}")
                print(f"Rating: {course_info['rating']} ({course_info['ratingCount']} ratings)")
                print(f"Skills: {course_info['skills']}")
                print(f"Description: {course_info['description']}")

            # Optionally save the full response to a JSON file
            with open(f"{slug}_details.json", "w") as f:
                json.dump(response, f, indent=2)
            print(f"Full details saved to {slug}_details.json")
        else:
            print(f"Failed to get details for {slug}")

if __name__ == "__main__":
    main()