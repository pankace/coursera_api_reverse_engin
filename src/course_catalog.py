import requests
import json
import pandas as pd
import os
import time
import re
from datetime import datetime

def extract_coursera_courses(query_params=None, limit=20, max_retries=3):
    """
    Extract course data from Coursera's API with improved error handling and debugging
    
    Args:
        query_params (dict, optional): Additional query parameters
        limit (int, optional): Maximum number of courses to retrieve
        max_retries (int, optional): Number of retry attempts per endpoint
        
    Returns:
        list: List of course dictionaries or empty list if failed
    """
    # Coursera has multiple potential endpoints we can try
    endpoints = [
        "https://www.coursera.org/api/catalogResults.v2",    # Standard catalog results API
        "https://www.coursera.org/api/courses.v1",           # Courses API (backup)
        "https://www.coursera.org/api/browse/courses"        # Browse courses API (backup)
    ]

    # More complete headers to mimic browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Origin": "https://www.coursera.org",
        "Referer": "https://www.coursera.org/courses",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }

    # Base query parameters
    params = {
        "start": 0,
        "limit": limit,
        "query": "",
        "sort": "relevance",
        "fields": "name,slug,description,partnerIds,partners.v1(name),skills,workload,rating,certificates"
    }

    if query_params:
        params.update(query_params)

    # Try each endpoint with retries
    for endpoint in endpoints:
        for attempt in range(max_retries):
            try:
                print(f"Trying endpoint {endpoint} (attempt {attempt+1}/{max_retries})...")
                response = requests.get(endpoint, headers=headers, params=params)

                print(f"Response status code: {response.status_code}")

                if response.status_code != 200:
                    print(f"Error: Received status code {response.status_code}")
                    if attempt < max_retries - 1:
                        print(f"Retrying in {2 ** attempt} seconds...")
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        print(f"Failed after {max_retries} attempts with endpoint {endpoint}")
                        break

                # Debug info: Print the first 100 characters of the response
                print(f"Response preview: {response.text[:100]}...")

                # Parse the JSON
                data = response.json()

                # Extract course data from the response
                courses = []

                # Different APIs have different response structures, handle each case
                if "elements" in data:
                    # Standard catalog API structure
                    for element in data.get("elements", []):
                        courses.append({
                            "id": element.get("id", ""),
                            "name": element.get("name", ""),
                            "slug": element.get("slug", ""),
                            "description": element.get("description", ""),
                            "partnerNames": [p.get("name", "") for p in element.get("partners", [])],
                            "skills": [s.get("name", "") for s in element.get("skills", [])],
                            "avgLearningHours": element.get("workload", ""),
                            "rating": element.get("rating", "")
                        })
                elif "linked" in data and "courses.v1" in data.get("linked", {}):
                    # Alternative API structure
                    for course in data["linked"]["courses.v1"]:
                        courses.append({
                            "id": course.get("id", ""),
                            "name": course.get("name", ""),
                            "slug": course.get("slug", ""),
                            "description": course.get("description", ""),
                            "partnerNames": course.get("partnerNames", []),
                            "skills": course.get("topicIds", []),  # May need transformation
                            "avgLearningHours": course.get("workload", ""),
                            "rating": course.get("rating", "")
                        })

                if courses:
                    print(f"Successfully extracted {len(courses)} courses")
                    return courses
                else:
                    print("No courses found in response data structure")
                    print(f"Response keys: {list(data.keys())}")
                    if attempt < max_retries - 1:
                        print(f"Retrying in {2 ** attempt} seconds...")
                        time.sleep(2 ** attempt)
                    else:
                        break

            except requests.exceptions.RequestException as e:
                print(f"Network error: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {2 ** attempt} seconds...")
                    time.sleep(2 ** attempt)
                else:
                    print(f"Failed after {max_retries} attempts with endpoint {endpoint}")
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print(f"Raw response (first 200 chars): {response.text[:200]}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {2 ** attempt} seconds...")
                    time.sleep(2 ** attempt)
                else:
                    print(f"Failed after {max_retries} attempts with endpoint {endpoint}")

    # If we've tried all endpoints and still failed, try a completely different approach
    print("All API endpoints failed. Trying to scrape course data from HTML...")

    try:
        # Fallback to getting course data from the browse page
        browse_url = "https://www.coursera.org/browse/data-science"

        print(f"Fetching HTML from {browse_url}...")
        response = requests.get(browse_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        })

        if response.status_code == 200:
            print("Successfully fetched course browse page")

            # Look for JSON data in the HTML (common pattern in modern websites)
            html = response.text

            # A common pattern is to have a script tag with JSON data
            json_matches = re.findall(r'<script id="initialState" type="application/json">(.*?)</script>', html)

            if json_matches:
                print("Found initialState JSON data in the page")
                try:
                    initial_data = json.loads(json_matches[0])

                    # Extract courses from the initial state data
                    # The exact path will depend on the structure; this is a common pattern
                    courses = []

                    if "browse" in initial_data and "courses" in initial_data["browse"]:
                        raw_courses = initial_data["browse"]["courses"]
                        for course_id, course_data in raw_courses.items():
                            courses.append({
                                "id": course_id,
                                "name": course_data.get("name", ""),
                                "slug": course_data.get("slug", ""),
                                "description": course_data.get("description", ""),
                                "partnerNames": [p.get("name", "") for p in course_data.get("partners", [])],
                                "skills": course_data.get("skills", []),
                                "avgLearningHours": course_data.get("workload", ""),
                                "rating": course_data.get("rating", "")
                            })

                    if courses:
                        print(f"Successfully extracted {len(courses)} courses from HTML")
                        return courses
                    else:
                        print("Could not find course data in the initialState JSON")
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON from HTML: {e}")
            else:
                print("Could not find initialState JSON in the HTML")
        else:
            print(f"Failed to fetch HTML: Status code {response.status_code}")

    except Exception as e:
        print(f"Error in HTML fallback method: {e}")

    # If all methods fail, return an empty list
    print("All extraction methods failed. Could not retrieve course data.")
    return []

def convert_to_csv(courses):
    """
    Convert course data to a pandas DataFrame and save as CSV
    
    Args:
        courses (list): List of course dictionaries
        
    Returns:
        str: Path to the saved CSV file or None if failed
    """
    if not courses:
        print("No courses to convert to CSV")
        return None

    # Normalize data and handle nested fields
    processed_courses = []

    for course in courses:
        course_data = {
            "id": course.get("id", ""),
            "name": course.get("name", ""),
            "slug": course.get("slug", ""),
            "description": course.get("description", "").replace("\n", " ").replace("\r", " "),  # Remove line breaks
            "learning_hours": course.get("avgLearningHours", ""),
            "partners": ", ".join(course.get("partnerNames", [])),
            "skills": ", ".join(course.get("skills", [])),
            "rating": course.get("rating", "")
        }
        processed_courses.append(course_data)

    # Create DataFrame
    df = pd.DataFrame(processed_courses)

    # Generate a timestamp for the filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"coursera_courses_{timestamp}.csv"

    # Save as CSV
    df.to_csv(file_path, index=False, encoding='utf-8')
    print(f"Data saved to {file_path}")

    return file_path