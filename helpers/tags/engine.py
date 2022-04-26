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
            'author_mention': ctx.author.mention,
            'author_name': ctx.author.name,
            'author_id': ctx.author.id,
            'author_discriminator': ctx.author.discriminator,
            'author_avatar_url': ctx.author.display_avatar.url,
        }

    def __getitem__(self, key: str) -> str | int:
        return self.substitute.get(key)
    
    def __setitem__(self, key: str, value: str) -> None:
        self.substitutes[key] = value

    def substitute(self, text: str) -> str:

        new_text = Template(text)
        return new_text.safe_substitute(self.substitutes)