import datetime
import os
import pickle
import re
from typing import List

import discord
from discord.ext import commands, tasks

utc = datetime.timezone.utc


'''class Menu(discord.ui.View):
    def __init__(self, id: int, type: str):
        """
        Initialize the Ranking UI

        Parameters
        ----------
        id : int
            Id of the requested user
        type : str
            Type of stats
        """
        super().__init__()

        self.tab_index = -1

        self.value = None
        self.id = id
        self.type = type
        self.view = "all"
        self.list = ["credit", "xp", "current streak", "highest streak", "games played", "games won", "average guesses"]
        for index, type in enumerate(self.list):
            if self.type == type:
                self.index = index

    @discord.ui.button(label=">", style=discord.ButtonStyle.red, custom_id=">")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Show to UI for the current selected stats and show the next stat option

        Parameters
        ----------
        interaction : discord.Interaction
            Used to handle button interaction
        button : discord.ui.Button
            Button object
        """
        self.index = (self.index + 1) % len(self.list)
        self.type = self.list[self.index]
        button.label = self.list[(self.index + 1) % len(self.list)].capitalize()

        previous_button = [x for x in self.children if x.custom_id == "<"][0]
        previous_button.label = self.list[(self.index - 1) % len(self.list)].capitalize()

        if self.view == "all":
            datas, title, currency = self.get_all_data()
        elif self.view == "month":
            datas, title, currency = self.get_month_data()
        embed = await self.make_embed(datas, title, currency)
        await interaction.response.edit_message(embed=embed, view=self)

        if self.tab_index == '''


class Activity:
    def __init__(self, date, time, name):
        self.date = date
        self.time = time
        self.name = name
        self.participating_individuals = set()

    def get_string_representation(self):
        # TODO remove
        return f'{self.name} will take place on {self.date.strftime("%d/%m/%Y")} at {self.time}h'

    def get_message_representation(self):
        return f'{self.name}: {self.time} ({convert_date_and_time_to_unix_time(datetime.datetime.combine(self.date, self.time))})'

    def __lt__(self, other):
        if self.date != other.date:
            return self.date < other.date

        if self.time != other.time:
            return self.time < other.time

        return self.name < other.name

    def __eq__(self, other):
        return self.date == other.date and self.time == other.time and self.name == other.name


class Activities:
    def __init__(self):
        self.activities: List[Activity] = []

    def __str__(self):
        # TODO remove
        return '\n'.join(list(map(lambda activity: activity.get_string_representation(), self.activities)))

    def add_activity(self, new_activity: Activity):
        for index, activity in enumerate(self.activities):
            if new_activity == activity:
                return "This activity already exists!"
            if new_activity < activity:
                self.activities.insert(index, new_activity)
                return "Activity added!"

        self.activities.append(new_activity)

        return "Activity added!"

    def remove_activities_from_the_past(self):
        index = 0

        while index < len(self.activities) and datetime.datetime.combine(self.activities[index].date, self.activities[index].time) <= datetime.datetime.now() - datetime.timedelta(days=1):
            index += 1

        self.activities = self.activities[index:]

    def remove_activity(self, date, time, name):
        index = 0

        while index < len(self.activities) and (self.activities[index].date != date or self.activities[index].time != time or self.activities[index].name != name):
            index += 1

        if index < len(self.activities):
            del self.activities[index]
            return "Activity deleted!"

        return "This activity does not exist!"

    def get_string_of_participants_of_activity(self, activity_index):
        return '\n'.join(list(sorted(self.activities[activity_index].participating_individuals)))


def write_activities_to_file(output_file: str, activities: Activities):
    """
    Write an Activities object to a pickle file.

    :param output_file: The output file.
    :param activities: The activities.
    """
    with open(output_file, 'wb') as file:
        pickle.dump(activities, file)


def load_activities_from_file(input_file: str):
    """
    Read an Activities object from a pickle file.

    :param input_file: The input file.

    :return: The Activities object.
    """
    with open(input_file, 'rb') as file:
        activities = pickle.load(file)

    return activities


def string_to_date(date_string: str) -> datetime.date:
    """
    Convert a string "day/month/year" to a date instance.

    :param date_string: The date.

    :return: The date instance.
    """
    date_format = "%d/%m/%Y"
    return datetime.datetime.strptime(date_string, date_format).date()


def string_to_time(time_string: str) -> datetime.time:
    """
    Convert a string "hours:minutes" to a time instance.

    :param time_string: The time.

    :return: The time instance.
    """
    time_format = "%H:%M"
    return datetime.datetime.strptime(time_string, time_format).time()


def convert_date_and_time_to_unix_time(date_and_time):
    # Convert to Unix timestamp
    unix_timestamp = int(date_and_time.timestamp())
    return f'<t:{unix_timestamp}:R>'


class ActivitiesCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.filename = 'activity_dates.pkl'
        self.check_loop.start()

    @tasks.loop(time=datetime.time(hour=23, minute=00, tzinfo=utc))
    async def check_loop(self):
        activities = load_activities_from_file(self.filename)
        activities.remove_activities_from_the_past()
        write_activities_to_file(self.filename, activities)

    @check_loop.before_loop
    async def before_printer(self):
        await self.client.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        if not os.path.exists(self.filename):
            write_activities_to_file(self.filename, Activities())
            print(f"{self.filename} created")

    @commands.command(usage="!addactivity <date> <time> <name>",
                      description="Add activity to list of activities",
                      help="!addactivity 15/12/2024 18:30 Yammi Yammi diner",
                      aliases=['aa'])
    async def addactivity(self, ctx, date, time, *, name):
        if not re.match("[0-3][0-9]/[0-1][0-9]/[0-9]{4}", date):
            await ctx.send("Date has to be DD/MM/YYYY, try again.")
            return
        if not re.match("^(?:[01]\d|2[0-3]):[0-5]\d$", time):
            await ctx.send("Time has to be HH:MM, try again.")
            return

        activity_date, activity_time = string_to_date(date), string_to_time(time)

        if datetime.datetime.combine(activity_date, activity_time) <= datetime.datetime.now():
            await ctx.send("Unfortunately, we cannot go back to the past!")
            return

        activities = load_activities_from_file(self.filename)
        message = activities.add_activity(Activity(activity_date, activity_time, name))
        write_activities_to_file(self.filename, activities)

        await ctx.send(message)

    @commands.command(usage="!listactivities",
                      description="List all activities",
                      help="!listactivities",
                      aliases=['la'])
    async def listactivities(self, ctx):
        activities_obj: Activities = load_activities_from_file(self.filename)

        if len(activities_obj.activities) == 0:
            await ctx.send("No activities planned!")

        messages = []

        current_activity = activities_obj.activities[0]
        current_date = current_activity.date
        current_date_string = current_date.strftime("%d/%m/%Y")

        message = [f"**__{current_date_string}:__**\n{current_activity.get_message_representation()}"]
        message_length = len(message[0])

        for current_activity in activities_obj.activities[1:]:
            if message_length > 2000:
                embed = discord.Embed(title=f"Upcoming activities", description='\n'.join(message))
                messages.append(embed)

                if current_activity.date != current_date:
                    current_date = current_activity.date
                    current_date_string = current_date.strftime("%d/%m/%Y")

                message_length = 0
                message = [f"\n**__{current_date_string}:__**\n{current_activity.get_message_representation()}"]
            elif current_activity.date != current_date:
                current_date = current_activity.date
                current_date_string = current_date.strftime("%d/%m/%Y")

                message_representation = f"\n**__{current_date_string}:__**\n{current_activity.get_message_representation()}"
                message_length += len(message_representation)
                message.append(message_representation)
            else:
                message_representation = current_activity.get_message_representation()
                message_length += len(message_representation)
                message.append(message_representation)

        if message_length > 0:
            embed = discord.Embed(title=f"Upcoming activities", description='\n'.join(message))
            messages.append(embed)

        for embed in messages:
            await ctx.send(embed=embed)

    @commands.command(usage="!deleteactivity <date> <time> <name>",
                      description="Delete activity from the list of activities",
                      help="!deleteactivity 15/12/2024 18:30 Yammi Yammi diner",
                      aliases=['da'])
    async def deleteactivity(self, ctx, date, time, *, name):
        if not re.match("[0-3][0-9]/[0-1][0-9]/[0-9]{4}", date):
            await ctx.send("Date has to be DD/MM/YYYY, try again.")
            return
        if not re.match("^(?:[01]\d|2[0-3]):[0-5]\d$", time):
            await ctx.send("Time has to be HH:MM, try again.")
            return

        activity_date, activity_time = string_to_date(date), string_to_time(time)

        activities = load_activities_from_file(self.filename)
        message = activities.remove_activity(activity_date, activity_time, name)
        write_activities_to_file(self.filename, activities)

        await ctx.send(message)


# Allows to connect cog to bot
async def setup(client):
    await client.add_cog(ActivitiesCog(client))
