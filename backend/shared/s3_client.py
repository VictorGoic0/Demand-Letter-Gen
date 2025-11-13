"""
S3 client for document storage operations.
Handles file uploads, downloads, deletions, and presigned URL generation.
"""
import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError, BotoCoreError

# Configure logging
logger = logging.getLogger(__name__)


class S3Client:
    """S3 client for managing document storage operations."""

    def __init__(
        self,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: Optional[str] = None,
    ):
        """
        Initialize S3 client with AWS credentials.
        
        In Lambda: Uses IAM role automatically
        In local dev: Uses explicit credentials from env vars
        
        Args:
            aws_access_key_id: AWS access key ID (defaults to env var)
            aws_secret_access_key: AWS secret access key (defaults to env var)
            region_name: AWS region name (defaults to env var)
        """
        # Detect if running in Lambda
        is_lambda = 'AWS_EXECUTION_ENV' in os.environ
        
        if is_lambda:
            # Lambda environment - use IAM role (no credentials)
            self.region_name = region_name or os.getenv('AWS_REGION', 'us-east-2')
            self.client = boto3.client(
                's3',
                region_name=self.region_name
            )
            logger.info("S3 client initialized with IAM role for Lambda")
        else:
            # Local development - use explicit credentials
            self.aws_access_key_id = aws_access_key_id or os.getenv('AWS_ACCESS_KEY_ID')
            self.aws_secret_access_key = aws_secret_access_key or os.getenv('AWS_SECRET_ACCESS_KEY')
            self.region_name = region_name or os.getenv('AWS_REGION', 'us-east-2')
            self.client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name
            )
            logger.info("S3 client initialized with explicit credentials for local dev")

    def upload_file(
        self,
        file_path: str,
        bucket_name: str,
        s3_key: str,
        metadata: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Upload a file to S3.
        
        Args:
            file_path: Path to the local file to upload
            bucket_name: Name of the S3 bucket
            s3_key: Key (path) for the file in S3
            metadata: Optional metadata dictionary
            content_type: Optional content type (MIME type)
            
        Returns:
            Dict containing upload details (bucket, key, url)
            
        Raises:
            FileNotFoundError: If the local file doesn't exist
            ClientError: If S3 operation fails
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Prepare extra args
            extra_args = {}
            if metadata:
                extra_args["Metadata"] = metadata
            if content_type:
                extra_args["ContentType"] = content_type
            
            # Upload file
            self.client.upload_file(
                file_path,
                bucket_name,
                s3_key,
                ExtraArgs=extra_args if extra_args else None
            )
            
            logger.info(f"File uploaded successfully: s3://{bucket_name}/{s3_key}")
            
            return {
                "bucket": bucket_name,
                "key": s3_key,
                "url": f"s3://{bucket_name}/{s3_key}",
                "region": self.region_name,
            }
            
        except ClientError as e:
            logger.error(f"Failed to upload file to S3: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during file upload: {str(e)}")
            raise

    def upload_fileobj(
        self,
        file_obj,
        bucket_name: str,
        s3_key: str,
        metadata: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Upload a file object to S3 (useful for in-memory files).
        
        Args:
            file_obj: File-like object to upload
            bucket_name: Name of the S3 bucket
            s3_key: Key (path) for the file in S3
            metadata: Optional metadata dictionary
            content_type: Optional content type (MIME type)
            
        Returns:
            Dict containing upload details (bucket, key, url)
            
        Raises:
            ClientError: If S3 operation fails
        """
        try:
            # Prepare extra args
            extra_args = {}
            if metadata:
                extra_args["Metadata"] = metadata
            if content_type:
                extra_args["ContentType"] = content_type
            
            # Upload file object
            self.client.upload_fileobj(
                file_obj,
                bucket_name,
                s3_key,
                ExtraArgs=extra_args if extra_args else None
            )
            
            logger.info(f"File object uploaded successfully: s3://{bucket_name}/{s3_key}")
            
            return {
                "bucket": bucket_name,
                "key": s3_key,
                "url": f"s3://{bucket_name}/{s3_key}",
                "region": self.region_name,
            }
            
        except ClientError as e:
            logger.error(f"Failed to upload file object to S3: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during file object upload: {str(e)}")
            raise

    def download_file(
        self,
        bucket_name: str,
        s3_key: str,
        destination_path: str,
    ) -> str:
        """
        Download a file from S3 to local filesystem.
        
        Args:
            bucket_name: Name of the S3 bucket
            s3_key: Key (path) of the file in S3
            destination_path: Local path to save the downloaded file
            
        Returns:
            Path to the downloaded file
            
        Raises:
            ClientError: If S3 operation fails
        """
        try:
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            # Download file
            self.client.download_file(bucket_name, s3_key, destination_path)
            
            logger.info(f"File downloaded successfully: {destination_path}")
            return destination_path
            
        except ClientError as e:
            logger.error(f"Failed to download file from S3: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during file download: {str(e)}")
            raise

    def download_fileobj(
        self,
        bucket_name: str,
        s3_key: str,
        file_obj,
    ) -> None:
        """
        Download a file from S3 to a file object.
        
        Args:
            bucket_name: Name of the S3 bucket
            s3_key: Key (path) of the file in S3
            file_obj: File-like object to write the downloaded content
            
        Raises:
            ClientError: If S3 operation fails
        """
        try:
            self.client.download_fileobj(bucket_name, s3_key, file_obj)
            logger.info(f"File downloaded to object: s3://{bucket_name}/{s3_key}")
            
        except ClientError as e:
            logger.error(f"Failed to download file object from S3: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during file object download: {str(e)}")
            raise

    def delete_file(
        self,
        bucket_name: str,
        s3_key: str,
    ) -> Dict[str, str]:
        """
        Delete a file from S3.
        
        Args:
            bucket_name: Name of the S3 bucket
            s3_key: Key (path) of the file in S3
            
        Returns:
            Dict with deletion confirmation
            
        Raises:
            ClientError: If S3 operation fails
        """
        try:
            self.client.delete_object(Bucket=bucket_name, Key=s3_key)
            logger.info(f"File deleted successfully: s3://{bucket_name}/{s3_key}")
            
            return {
                "bucket": bucket_name,
                "key": s3_key,
                "status": "deleted",
            }
            
        except ClientError as e:
            logger.error(f"Failed to delete file from S3: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during file deletion: {str(e)}")
            raise

    def generate_presigned_url(
        self,
        bucket_name: str,
        s3_key: str,
        expiration: int = 3600,
        http_method: str = "GET",
    ) -> str:
        """
        Generate a presigned URL for temporary access to an S3 object.
        
        Args:
            bucket_name: Name of the S3 bucket
            s3_key: Key (path) of the file in S3
            expiration: URL expiration time in seconds (default: 1 hour)
            http_method: HTTP method for the presigned URL (GET, PUT, etc.)
            
        Returns:
            Presigned URL string
            
        Raises:
            ClientError: If S3 operation fails
        """
        try:
            # Map HTTP method to S3 client method
            method_map = {
                "GET": "get_object",
                "PUT": "put_object",
                "DELETE": "delete_object",
            }
            
            client_method = method_map.get(http_method.upper(), "get_object")
            
            url = self.client.generate_presigned_url(
                ClientMethod=client_method,
                Params={"Bucket": bucket_name, "Key": s3_key},
                ExpiresIn=expiration,
            )
            
            logger.info(f"Presigned URL generated for: s3://{bucket_name}/{s3_key}")
            return url
            
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating presigned URL: {str(e)}")
            raise

    def check_bucket_exists(self, bucket_name: str) -> bool:
        """
        Check if an S3 bucket exists and is accessible.
        
        Args:
            bucket_name: Name of the S3 bucket
            
        Returns:
            True if bucket exists and is accessible, False otherwise
        """
        try:
            self.client.head_bucket(Bucket=bucket_name)
            logger.info(f"Bucket exists and is accessible: {bucket_name}")
            return True
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "404":
                logger.warning(f"Bucket does not exist: {bucket_name}")
            elif error_code == "403":
                logger.warning(f"Bucket exists but access denied: {bucket_name}")
            else:
                logger.error(f"Error checking bucket: {str(e)}")
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error checking bucket: {str(e)}")
            return False

    def list_files(
        self,
        bucket_name: str,
        prefix: str = "",
        max_keys: int = 1000,
    ) -> list:
        """
        List files in an S3 bucket (useful for debugging).
        
        Args:
            bucket_name: Name of the S3 bucket
            prefix: Optional prefix to filter objects
            max_keys: Maximum number of keys to return
            
        Returns:
            List of object dictionaries with keys, sizes, and timestamps
            
        Raises:
            ClientError: If S3 operation fails
        """
        try:
            response = self.client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys,
            )
            
            objects = []
            if "Contents" in response:
                for obj in response["Contents"]:
                    objects.append({
                        "key": obj["Key"],
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"],
                        "etag": obj["ETag"],
                    })
            
            logger.info(f"Listed {len(objects)} objects in bucket: {bucket_name}")
            return objects
            
        except ClientError as e:
            logger.error(f"Failed to list files in S3: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error listing files: {str(e)}")
            raise

    def get_object_metadata(
        self,
        bucket_name: str,
        s3_key: str,
    ) -> Dict[str, Any]:
        """
        Get metadata for an S3 object.
        
        Args:
            bucket_name: Name of the S3 bucket
            s3_key: Key (path) of the file in S3
            
        Returns:
            Dict containing object metadata
            
        Raises:
            ClientError: If S3 operation fails
        """
        try:
            response = self.client.head_object(Bucket=bucket_name, Key=s3_key)
            
            metadata = {
                "content_length": response.get("ContentLength"),
                "content_type": response.get("ContentType"),
                "last_modified": response.get("LastModified"),
                "etag": response.get("ETag"),
                "metadata": response.get("Metadata", {}),
            }
            
            logger.info(f"Retrieved metadata for: s3://{bucket_name}/{s3_key}")
            return metadata
            
        except ClientError as e:
            logger.error(f"Failed to get object metadata: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting metadata: {str(e)}")
            raise


# Singleton instance for easy access
_s3_client_instance: Optional[S3Client] = None


def get_s3_client() -> S3Client:
    """
    Get or create a singleton S3 client instance.
    
    Returns:
        S3Client instance
    """
    global _s3_client_instance
    if _s3_client_instance is None:
        _s3_client_instance = S3Client()
    return _s3_client_instance

