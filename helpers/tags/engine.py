from string import Template
from discord.ext.commands import Context

class TagEngine:

    """
    Handles the tag engine.

    Usage:
    ```py
    >>> from helpers.tag.engine import TagEngine
    >>> engine = TagEngine(ctx)
    >>> engine.substitute('Hello, $author_name!')
    'Hello, sift!'
    ```
    """
    
    def __init__(self, ctx: Context, substitutes: dict=None) -> None:
        self.substitutes = substitutes if substitutes else {
            '{user.mention}': ctx.author.mention,
            '{user.name}': ctx.author.name,
            '{user.id}': ctx.author.id,
            '{user.discriminator}': ctx.author.discriminator,
            '{user.avatar.url}': ctx.author.display_avatar.url,
        }

    def __getitem__(self, key: str) -> str | int:
        return self.substitute.get(key)
    
    def __setitem__(self, key: str, value: str) -> None:
        self.substitutes[key] = value

    def substitute(self, text: str) -> str:
        for key, value in self.substitutes.items():
            text = text.replace(key, str(value))
        return text
