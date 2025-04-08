import os
import mimetypes
from datetime import datetime

def upload_to_gcs(local_file_path, bucket_name, destination_blob_name=None,
                  make_public=False, content_type=None, metadata=None):
    """
    Uploads a file to a Google Cloud Storage bucket
    
    Args:
        local_file_path (str): Path to the local file to upload
        bucket_name (str): Name of the GCS bucket
        destination_blob_name (str, optional): Name to give the uploaded file in GCS
        make_public (bool, optional): Whether to make the uploaded file public
        content_type (str, optional): MIME type of the file
        metadata (dict, optional): Additional metadata to attach to the file
        
    Returns:
        dict: Information about the uploaded file or None if upload failed
    """
    try:
        # Import Google Cloud Storage library here to make it optional
        from google.cloud import storage
        
        # If destination blob name is not specified, use the file name
        if destination_blob_name is None:
            destination_blob_name = os.path.basename(local_file_path)

        # Detect content type if not specified
        if content_type is None:
            content_type, _ = mimetypes.guess_type(local_file_path)
            if content_type is None:
                content_type = 'application/octet-stream'

        # Initialize the client
        storage_client = storage.Client()

        # Get the bucket
        bucket = storage_client.bucket(bucket_name)

        # Create a blob and upload the file
        blob = bucket.blob(destination_blob_name)

        # Set content type and metadata
        blob.content_type = content_type
        if metadata:
            blob.metadata = metadata

        # Upload the file
        blob.upload_from_filename(local_file_path)

        # Make public if requested
        if make_public:
            blob.make_public()
            url = blob.public_url
        else:
            url = None

        gs_path = f"gs://{bucket_name}/{destination_blob_name}"
        print(f"File {local_file_path} uploaded to {gs_path}")

        return {
            'url': url,
            'path': gs_path,
            'bucket': bucket_name,
            'blob': destination_blob_name
        }

    except ImportError:
        print("Error: google-cloud-storage library not installed.")
        print("Please install it using: pip install google-cloud-storage")
        return None
    except Exception as e:
        print(f"Error uploading to Google Cloud Storage: {e}")
        return None

def ensure_bucket_exists(bucket_name, location="us-central1", user_email=None):
    """
    Create the bucket if it doesn't exist and optionally grant access to a specific user
    
    Args:
        bucket_name (str): Name of the GCS bucket
        location (str, optional): GCS location (region) for the bucket
        user_email (str, optional): Email address to grant viewer access
        
    Returns:
        bool: Whether the bucket exists and is accessible
    """
    try:
        # Import Google Cloud Storage library here to make it optional
        from google.cloud import storage
        
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)

        if not bucket.exists():
            print(f"Creating bucket {bucket_name}...")
            bucket = storage_client.create_bucket(bucket_name, location=location)
            print(f"Bucket {bucket_name} created")
        else:
            print(f"Bucket {bucket_name} already exists")

        # Set IAM policy to grant access to a user if specified
        if user_email:
            policy = bucket.get_iam_policy()

            # Check if the binding already exists to avoid duplicates
            user_has_access = False
            for binding in policy.bindings:
                if binding.get("role") == "roles/storage.objectViewer" and f"user:{user_email}" in binding.get("members", []):
                    user_has_access = True
                    break

            if not user_has_access:
                policy.bindings.append({
                    "role": "roles/storage.objectViewer",
                    "members": [f"user:{user_email}"]
                })
                bucket.set_iam_policy(policy)
                print(f"Access granted to {user_email}")
            else:
                print(f"{user_email} already has access")

        return True

    except ImportError:
        print("Error: google-cloud-storage library not installed.")
        print("Please install it using: pip install google-cloud-storage")
        return False
    except Exception as e:
        print(f"Error with bucket operations: {e}")
        return False