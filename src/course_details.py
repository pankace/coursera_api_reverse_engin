import requests
import json

def get_course_details(course_slug):
    """
    Gets detailed information for a specific course using its slug.

    Args:
        course_slug (str): The course slug (from the URL)

    Returns:
        dict: Detailed course information
    """
    url = "https://www.coursera.org/graphql-gateway"
    operation_name = "CDPPageQuery"

    # Headers to mimic browser request
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json",
        "Origin": "https://www.coursera.org",
        "Referer": f"https://www.coursera.org/learn/{course_slug}"
    }

    # GraphQL query based on the provided schema
    query = """
    query CDPPageQuery($slug: String!) {
      XdpV1Resource {
        slug(productType: "COURSE", slug: $slug) {
          elements {
            name
            id
            slug
            xdpMetadata {
              ... on XdpV1_cdpMetadataMember {
                cdpMetadata {
                  id
                  avgLearningHoursAdjusted
                  level
                  certificates
                  courseStatus
                  domains {
                    domainId
                    domainName
                    subdomainName
                    subdomainId
                  }
                  primaryLanguages
                  skills
                  photoUrl
                  name
                  slug
                  description
                  workload
                  partners {
                    id
                    name
                    shortName
                    logo
                  }
                  instructors {
                    id
                    fullName
                    photo
                    title
                  }
                  ratings {
                    averageFiveStarRating
                    ratingCount
                    commentCount
                  }
                }
              }
            }
          }
        }
      }
    }
    """

    # Request body
    payload = {
        "operationName": operation_name,
        "variables": {"slug": course_slug},
        "query": query
    }

    # Make the request
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def extract_basic_info(response_data):
    """
    Extract and print basic information from the API response
    
    Args:
        response_data (dict): The API response from get_course_details
        
    Returns:
        dict: Extracted course information or None if extraction fails
    """
    try:
        # Navigate through the response structure
        elements = response_data["data"]["XdpV1Resource"]["slug"]["elements"]
        if not elements:
            print("No course found")
            return None

        course = elements[0]
        metadata = course["xdpMetadata"]["cdpMetadata"]

        # Extract basic information
        info = {
            "name": metadata["name"],
            "description": metadata["description"][:100] + "..." if metadata["description"] else "N/A",
            "level": metadata["level"],
            "workload": metadata["workload"],
            "skills": ", ".join(metadata["skills"][:5]) + "..." if len(metadata["skills"]) > 5 else ", ".join(metadata["skills"]),
            "partners": [p["name"] for p in metadata["partners"]],
            "instructors": [i["fullName"] for i in metadata["instructors"]],
            "rating": metadata["ratings"]["averageFiveStarRating"] if "ratings" in metadata else "N/A",
            "ratingCount": metadata["ratings"]["ratingCount"] if "ratings" in metadata else "N/A"
        }

        return info
    except Exception as e:
        print(f"Error extracting information: {e}")
        return None