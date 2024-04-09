import random
import string

import discord


def random_id(length=8):
    """
    Generate a random string of fixed length
    """
    letters = string.digits
    return int("".join(random.choice(letters) for _ in range(length)))


class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(
        self, interaction: discord.Interaction, _: discord.ui.Button
    ):
        await interaction.response.send_message("Confirming", ephemeral=True)
        self.value = True
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, _: discord.ui.Button):
        await interaction.response.send_message("Cancelling", ephemeral=True)
        self.value = False
        self.stop()
