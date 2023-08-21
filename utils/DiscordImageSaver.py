import uuid
from os import path

import aiofiles
import aiohttp


class DiscordImageSaver:
    def __init__(self, url, user_id, destination_directory):
        self.url = url
        self.user_id = user_id
        self.destination_directory = destination_directory
        self.saved_image_name = None

    async def save_image_from_url(self):
        """Download and saves an image from a `https://cdn.discordapp.com/attachments` url
        """

        if not self.url.startswith("https://cdn.discordapp.com/attachments/"):
            return
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as response:
                    if not response.status == 200:
                        return
                        
                    image_extension = path.splitext(self.url)[-1]
                    image_name = f"user_id-{self.user_id}-uuid{uuid.uuid4().hex}{image_extension}"
                    destination_path = path.join(self.destination_directory, image_name)

                    async with aiofiles.open(destination_path, 'wb') as file:
                        await file.write(await response.read())

                    self.saved_image_name = image_name

        except Exception as e:
            print(f"An error occurred: {e}")

    @property
    def image_name(self):
        """The saved image's file name.

        Returns
        -------
        `str | none`
        """
        return self.saved_image_name