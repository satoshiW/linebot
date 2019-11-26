from PIL import Image

def date_the_image(src: str, desc: str) -> None:
    im = Image.open(src)
    
    s3_resource = boto3.resource("s3")
    s3_resource.Bucket(aws_s3_bucket).upload_file(message_id, message_id)
    
    s3_client = boto3.client("s3")
    s3_image_url = s3_client.generater_presigned_url(
           ClientMethod = "get_object",
           Params = {"Bucket": aws_s3_bucket, "Key": message_id},
           ExpiresIn = 10,
           HttpMethod = "GET"
    )
    """
    try:
    	exif = im._getexif()
    except AttributeError:
    	return {}
    	
    exif_table = {}
    for tag_id, value in exif.items():
    	tag = TAGS.get(tag_id, tag_id)
    	exif_table[tag] = value

    return exif_table.get("DateTimeOriginal")
    
    im.save(desc)"""