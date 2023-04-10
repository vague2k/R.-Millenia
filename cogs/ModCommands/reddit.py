import datetime
import logging

import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands import GroupCog

from millenia import Millenia
from utils.embed import create_embed_failure, create_embed_success
from utils.reddit import reddit_object

_logger = logging.getLogger(__name__)


utc = datetime.timezone.utc
time = datetime.time(hour=22, minute=0, second=0, tzinfo=utc)


@app_commands.guild_only()
class RedditPostsBackgroundTasks(GroupCog, group_name="reddit"):
    def __init__(self, bot: Millenia):
        self.bot = bot
        self.reddit = reddit_object()

    def cog_unload(self):
        self.my_task.stop()

    ### Command to START the daily tasks of posting a user chosen reddit thread in a user chosen channel ###
    @app_commands.command(name="starttask", description="Setup where you want to to send the hottest reddit posts")
    @app_commands.describe(
        channel="Which channel would you like this bot to send the daily reddit posts to?",
        subreddit="Which subreddit would like to post? **THIS IS CASE SENSITIVE**",
    )
    @commands.has_guild_permissions(manage_channels=True, manage_messages=True, view_audit_log=True)
    async def start_reddit_task(self, interaction: discord.Interaction, channel: discord.TextChannel, subreddit: str):
        if self.my_task.is_running() == False:
            self.subreddit = subreddit
            assert interaction.guild is not None

            subreddit_chosen_embed = create_embed_success(
                message=f"You hottest posts for the **r/{subreddit}** subreddit\nwill be sent to your channel of choice,**#{channel.name}**"
            )
            await interaction.response.send_message(embed=subreddit_chosen_embed, delete_after=60)
            user_chosen_channel = await interaction.guild.fetch_channel(channel.id)
            self.my_task.start(user_chosen_channel)

        else:
            current_loop_active_embed = create_embed_failure(
                message="It seems there's already a background task being looped through.\nIf you would like to cancel this task, use `/reddit <canceltask>`"
            )
            await interaction.response.send_message(embed=current_loop_active_embed, delete_after=60)

    ### Command to CANCEL the daily tasks of posting a user chosen reddit thread in a user chosen channel ###
    @app_commands.command(
        name="canceltask", description="Stop the current background task. Usually used if you want to change the subreddit"
    )
    @commands.has_guild_permissions(manage_channels=True, manage_messages=True, view_audit_log=True)
    async def stop_current_reddit_task(self, interaction: discord.Interaction):
        if self.my_task.is_running() == True:
            self.my_task.cancel()
            cancel_task_embed = create_embed_success(message="The current task has been canceled")
            await interaction.response.send_message(embed=cancel_task_embed, delete_after=60)

        else:
            no_task_active_embed = create_embed_failure(
                "There is no task currently running,\nif you'd like to start one considering using `/reddit <starttask>`"
            )
            await interaction.response.send_message(embed=no_task_active_embed, delete_after=60)

    @tasks.loop(seconds=10)
    async def my_task(self, ctx: commands.Context):
        user_chosen_subreddit = await self.reddit.subreddit(str(self.subreddit))
        hot = user_chosen_subreddit.hot(limit=2)

        submission_list = []
        async for submission in hot:
            if not submission.stickied:
                submission_list.append(submission)

        submissison_title = submission.title  # type: ignore
        submissison_url = submission.url  # type: ignore

        reddit_embed = discord.Embed(
            title=submissison_title,
            description=f"[Go to this subreddit!](https://www.reddit.com/r/{user_chosen_subreddit}/)",
            color=0xFC9723,
        )
        reddit_embed.set_image(url=submissison_url)
        reddit_embed.add_field(name="", value=f"Current hottest post from the r/{user_chosen_subreddit} subreddit!")
        reddit_embed.set_footer(
            text="If content is not visible, the attatched content is actually a **Video**. Go click it on it to watch it!"
        )

        await ctx.send(embed=reddit_embed)


async def setup(bot: Millenia):
    _logger.info("Loading cog reddit")
    await bot.add_cog(RedditPostsBackgroundTasks(bot))


async def teardown(_: Millenia):
    _logger.info("Unloading cog reddit")
