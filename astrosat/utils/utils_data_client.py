import boto3
import logging
import re

from collections import namedtuple
from botocore.exceptions import ClientError

from astrosat.conf import app_settings


BucketObjectTuple = namedtuple(
    "BucketObjectTuple",
    ["stream", "metadata"]
)


def set_boto3_logging_level(level=logging.CRITICAL):
    """
    playing w/ boto3 generates _loads_ of messages
    this lets me suppress that as needed
    """
    logger_patterns = re.compile("boto|boto3|urllib3|s3transfer")
    for logger_name in logging.Logger.manager.loggerDict.keys():
        if logger_patterns.match(logger_name):
            logging.getLogger(logger_name).setLevel(level)


class DataClient():

    client = None
    bucket = None

    def __init__(self, *args, **kwargs):

        logging_level = kwargs.pop("logging_level", logging.ERROR)
        set_boto3_logging_level(level=logging_level)

        assert app_settings.AWS_BUCKET_NAME and app_settings.AWS_ACCESS_KEY_ID and app_settings.AWS_SECRET_ACCESS_KEY

        self.client = boto3.client(
            "s3",
            aws_access_key_id=app_settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=app_settings.AWS_SECRET_ACCESS_KEY,
        )
        self.bucket = app_settings.AWS_BUCKET_NAME

    def get_all_matching_objects(self, pattern, metadata_only=False):
        """
        Gets all objects from the current bucket matching a regex pattern
        """

        pattern = re.compile(pattern)

        kwargs = {"Bucket": self.bucket}
        while True:
            response = self.client.list_objects_v2(**kwargs)
            for metadata_obj in response["Contents"]:
                key = metadata_obj["Key"]
                if pattern.match(key):
                    matching_obj = self.client.get_object(
                        Bucket=self.bucket,
                        Key=key
                    ) if not metadata_only else None
                    yield BucketObjectTuple(
                        matching_obj.get("Body") if not metadata_only else None,
                        metadata_obj,
                    )
            try:
                kwargs["ContinuationToken"] = response["NextContinuationToken"]
            except KeyError:
                break

    def get_first_matching_object(self, pattern, metadata_only=False):
        """
        Gets the first object from the current bucket matching a regex pattern
        """
        try:
            return next(self.get_all_matching_objects(pattern, metadata_only=metadata_only))
        except StopIteration:
            return None

    def get_object(self, key):
        """
        Gets an object from the current bucket w/ the specified key.
        Tries to get the key exactly, rather than treating it as a regex pattern
        (so this fn should be faster than the above 2 fns).
        """
        if key is not None:
            try:
                obj = self.client.get_object(
                    Bucket=self.bucket,
                    Key=key,
                )
                if obj:
                    return obj.get("Body")
            except ClientError as e:
                # if the key is wrong, don't return anthing...
                if e.response["Error"]["Code"] != "NoSuchKey":
                    # ...but if some other error ocurred, raise it
                    raise(e)

    def get_objects(self, key, metadata_only=True):
        """
        Gets all objects from the bucket directory w/ the specified key.
        Again, uses the exact key, rather than treating it as a regex pattern
        Also appends all tags to the metadata of the returned BucketObjectTuples
        """
        if key is not None:
            try:
                response = self.client.list_objects_v2(
                    Bucket=self.bucket,
                    Prefix=key,
                )
                if response["KeyCount"]:
                    objs = []
                    for obj in response["Contents"]:
                        if obj["Size"] > 0:  # (skip directories)
                            obj_key = obj["Key"]
                            obj_tags = {
                                obj_tagset["Key"]: obj_tagset["Value"]
                                for obj_tagset in self.client.get_object_tagging(
                                    Bucket=self.bucket,
                                    Key=obj_key,
                                )["TagSet"]  # tags are in "sets", hence this dictionary comprehension
                            }
                            assert "key" not in obj_tags, "object tagset must not use the reserved word 'key'"
                            obj_tags["key"] = obj_key
                            objs.append(
                                BucketObjectTuple(
                                    self.client.get_object(Bucket=self.bucket, Key=obj_key)["Body"] if not metadata_only else None,
                                    obj_tags,
                                )
                            )

                    return objs

            except ClientError as e:
                # if the key is wrong, don't return anything...
                if e.response["Error"]["Code"] != "NoSuchKey":
                    # ...but if some other error ocurred, raise it
                    raise(e)

    def get_data(self, pattern):
        """
        Returns a file-like object from the bucket
        """

        obj = self.get_first_matching_object(pattern, metadata_only=False)
        if obj:
            return BytesIO(obj.stream.read())

    def get_object_url(self, pattern):
        """
        Returns a url that the client can use to retrieve an otherwise protected object
        """

        method = "get_object"
        expiry = 1800  # half-an-hour

        obj = self.get_first_matching_object(pattern, metadata_only=True)
        if obj:
            url = self.client.generate_presigned_url(
                ClientMethod=method,
                ExpiresIn=expiry,
                Params={
                    "Bucket": self.bucket,
                    "Key": obj.metadata["Key"],
                }
            )
            return url
