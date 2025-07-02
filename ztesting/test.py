import uuid
from django.utils.text import slugify


base_slug = slugify("I am a boy")
unique_id = uuid.uuid4().hex[:6]
slug = f"{base_slug}-{unique_id}"

print(slug)
