from io import BytesIO
from zlib import decompressobj

from discord import Embed, Interaction, MessageReference
from discord.ext.commands import Context
from discord.ui import Button, View, button


class SphinxObjectFileReader:
    BUFSIZE = 16 * 1024

    def __init__(self, buffer: bytes):
        self.stream = BytesIO(buffer)

    def readline(self):
        return self.stream.readline().decode("utf-8")

    def skipline(self):
        self.stream.readline()

    def read_compressed_chunks(self):
        decompressor = decompressobj()
        while True:
            chunk = self.stream.read(self.BUFSIZE)
            if len(chunk) == 0:
                break
            yield decompressor.decompress(chunk)
        yield decompressor.flush()

    def read_compressed_lines(self):
        buf = b""
        for chunk in self.read_compressed_chunks():
            buf += chunk
            pos = buf.find(b"\n")
            while pos != -1:
                yield buf[:pos].decode("utf-8")
                buf = buf[pos + 1 :]
                pos = buf.find(b"\n")


class RTFMView(View):
    def __init__(
        self,
        reference: MessageReference,
        embed: Embed,
        context: Context,
    ):
        super().__init__()
        self.reference = reference
        self.embed = embed
        self.context = context

    async def interaction_check(self, interaction: Interaction):
        if interaction.user.id != self.context.author.id:
            return False
        return True

    async def start(self):
        await self.context.send(embed=self.embed, reference=self.reference, view=self)

    @button(emoji="🗑️")
    async def delete(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()

        await interaction.delete_original_message()
