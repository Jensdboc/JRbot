import datetime
import os
import pickle
import re
from typing import List, Tuple

import discord
from discord.ext import commands, tasks

utc = datetime.timezone.utc


class Activity:
    """
    This class contains the date, time and name of the activity and a dictionary that maps the ID of the participants to their name.
    """
    def __init__(self, date: datetime.date, time: datetime.time, name: str):
        self.date = date
        self.time = time
        self.name = name
        self.participating_individuals = dict()

    def get_string_representation(self, current_activity_index: int) -> str:
        """
        Obtain the string representation of an activity.

        :param current_activity_index: The index of the activity.

        :return: The string representation.
        """
        t = self.time.strftime('%H:%M')
        return f'({current_activity_index}) {self.name}: {t}h'

    def __lt__(self, other) -> bool:
        """
        Override the less than operator so that you can sort a list of activities.

        :param other: The other Activity object.

        :return: True if the object is smaller than the other one, else False.
        """
        if self.date != other.date:
            return self.date < other.date

        if self.time != other.time:
            return self.time < other.time

        return self.name < other.name

    def __eq__(self, other) -> bool:
        """
        Override the __eq__ operator so that you can sort a list of activities.

        :param other: The other Activity object.

        :return: True if the objects are equal, else False.
        """
        return self.date == other.date and self.time == other.time and self.name == other.name


class ActivitiesObj:
    """
    This class contains a list of Activity objects.
    """
    def __init__(self):
        self.activities: List[Activity] = []

    def add_activity(self, new_activity: Activity):
        """
        Add an activity to the list of activities if it doesn't exist yet.

        :param new_activity: The new activity object.

        :return: The status message.
        """
        for index, activity in enumerate(self.activities):
            if new_activity == activity:
                return "This activity already exists!"

            if new_activity < activity:
                self.activities.insert(index, new_activity)
                return "Activity added!"

        self.activities.append(new_activity)

        return "Activity added!"

    def remove_activities_from_the_past(self) -> None:
        """
        Remove all outdated activities.
        """
        index = 0

        while index < len(self.activities) and datetime.datetime.combine(self.activities[index].date, self.activities[index].time) <= datetime.datetime.now() - datetime.timedelta(days=1):
            index += 1

        self.activities = self.activities[index:]

    def remove_activity(self, activity_id: int) -> str:
        """
        Remove an activity.

        :param activity_id: The id of the activity.

        :return: The status message.
        """
        del self.activities[activity_id - 1]
        return "Activity deleted!"

    def get_string_of_participants_of_activity(self, activity_index: int) -> str:
        """
        Obtain the string representation of all participants of an activity.

        :param activity_index: The index of the activity in the activities list.

        :return: The string of participants.
        """
        return '\n'.join(list(sorted(map(lambda x: x[1], self.activities[activity_index].participating_individuals.items()))))

    def list_activities(self) -> List[Tuple[str, List[Tuple[str, int]]]]:
        """
        Obtain a list of pages/messages. Each page/message contains a title and another list that contains tuples: each tuple contains an activity string and the current number of participants.

        :return: The list of pages/messages.
        """
        messages = []

        current_activity_index = 1
        current_activity = self.activities[0]
        current_date = current_activity.date
        current_date_string = current_date.strftime("%d/%m/%Y")

        # start of first message
        message = [(f"**__{current_date_string}:__**\n{current_activity.get_string_representation(current_activity_index)}", len(current_activity.participating_individuals))]

        # get the message length: 16 for the ' (... participants)' part
        message_length = len(message[0][0]) + 16 + len(str(len(current_activity.participating_individuals)))

        page = 1

        for current_activity in self.activities[1:]:
            current_activity_index += 1
            # if message too large -> output
            if message_length > 750:
                messages.append((f'Upcoming activities {page}', message))

                page += 1

                # update the current date to sort the activities
                if current_activity.date != current_date:
                    current_date = current_activity.date
                    current_date_string = current_date.strftime("%d/%m/%Y")

                message = [(f"\n**__{current_date_string}:__**\n{current_activity.get_string_representation(current_activity_index)}", len(current_activity.participating_individuals))]
                message_length = (len(message[0][0]) + 16 + len(str(len(current_activity.participating_individuals))))
            elif current_activity.date != current_date:
                current_date = current_activity.date
                current_date_string = current_date.strftime("%d/%m/%Y")

                message_representation = f"\n**__{current_date_string}:__**\n{current_activity.get_string_representation(current_activity_index)}"
                message_length += (len(message_representation) + 16 + len(str(len(current_activity.participating_individuals))))
                message.append((message_representation, len(current_activity.participating_individuals)))
            else:
                message_representation = current_activity.get_string_representation(current_activity_index)
                message_length += (len(message_representation) + 16 + len(str(len(current_activity.participating_individuals))))
                message.append((message_representation, len(current_activity.participating_individuals)))

        if message_length > 0:
            messages.append((f'Upcoming activities {page}', message))

        return messages


def write_activities_to_file(output_file: str, activities_obj: ActivitiesObj) -> None:
    """
    Write an Activities object to a pickle file.

    :param output_file: The output file.
    :param activities_obj: The activities object.
    """
    with open(output_file, 'wb') as file:
        pickle.dump(activities_obj, file)


def load_activities_from_file(input_file: str) -> ActivitiesObj:
    """
    Read an Activities object from a pickle file.

    :param input_file: The input file.

    :return: The Activities object.
    """
    with open(input_file, 'rb') as file:
        activities_obj = pickle.load(file)

    return activities_obj


def string_to_date(date_string: str) -> datetime.date:
    """
    Convert a string "day/month/year" to a date object.

    :param date_string: The date.

    :return: The date object.
    """
    return datetime.datetime.strptime(date_string, "%d/%m/%Y").date()


def string_to_time(time_string: str) -> datetime.time:
    """
    Convert a string "hours:minutes" to a time object.

    :param time_string: The time.

    :return: The time object.
    """
    return datetime.datetime.strptime(time_string, "%H:%M").time()


def convert_date_and_time_to_unix_time(date_and_time: datetime.datetime, server_offset: int = -1) -> str:
    """
    Convert a datetime object to a unix timestamp.

    :param date_and_time: The datetime object.
    :param server_offset: The server offset.

    :return: The unix timestamp (as a string).
    """
    date_and_time += datetime.timedelta(hours=server_offset)
    return f'<t:{int(date_and_time.timestamp())}:R>'


def get_indices_of_activity(messages: List[Tuple[str, List[Tuple[str, int]]]], activity_index: int) -> Tuple[int, int]:
    """
    Obtain the message page where the activity occurs and the index on that page.

    :param messages: The pages/messages.
    :param activity_index: The activity index.

    :return: A tuple that represents the page and the index on that page.
    """
    page_index, index_on_page = 0, 0

    while activity_index != 0:
        if activity_index >= len(messages[page_index][1]):
            page_index += 1
            activity_index -= len(messages[page_index][1])
        else:
            index_on_page = activity_index
            activity_index = 0

    return page_index, index_on_page


def is_valid_date(date_string):
    try:
        datetime_object = datetime.datetime.strptime(date_string, '%d/%m/%Y')
        return True
    except ValueError:
        return False


class Activities(commands.Cog):
    """
    This class contains the filename in which the data is stored and the commands.
    """
    def __init__(self, client: discord.Client):
        self.client = client
        self.filename = 'activity_dates.pkl'
        self.check_loop.start()
        self.ping_users_loop.start()

    @tasks.loop(time=datetime.time(hour=23, minute=00, tzinfo=utc))
    async def check_loop(self) -> None:
        """
        Each day, remove all outdated activities at a certain time.
        """
        activities = load_activities_from_file(self.filename)
        activities.remove_activities_from_the_past()
        write_activities_to_file(self.filename, activities)

    @check_loop.before_loop
    async def before_check_loop(self):
        await self.client.wait_until_ready()

    @tasks.loop(time=datetime.time(hour=9, minute=00, tzinfo=utc))
    async def ping_users_loop(self):
        activities_obj = load_activities_from_file(self.filename)

        activity_index = 0

        guild_id = 764196816517464084
        guild = self.client.get_guild(guild_id)

        if guild:
            while activity_index < len(activities_obj.activities) and activities_obj.activities[activity_index].date == datetime.datetime.now().date():
                for participant_id, participant_name in activities_obj.activities[activity_index].participating_individuals.items():
                    member = guild.get_member(participant_id)
                    if member:
                        t = activities_obj.activities[activity_index].time.strftime('%H:%M')
                        embed = discord.Embed(title='There is an activity scheduled for you today!', description=f'{activities_obj.activities[activity_index].name}: {t}h')
                        await member.send(embed=embed)
                activity_index += 1

    @ping_users_loop.before_loop
    async def before_ping_users_loop(self):
        await self.client.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        Create the file in which the data will be stored.
        """
        if not os.path.exists(self.filename):
            write_activities_to_file(self.filename, ActivitiesObj())
            print(f"{self.filename} created")

    @commands.command(usage="!addactivity <date> <time> <name>",
                      description="Add activity to list of activities",
                      help="!addactivity 15/12/2024 18:30 Yammi Yammi diner",
                      aliases=['aa'])
    async def addactivity(self, ctx: commands.Context, date: str, time: str, *, name: str) -> None:
        """
        Add an activity to the list.

        :param ctx: The context.
        :param date: The date of the new activity.
        :param time: The time of the new activity.
        :param name: The name of the activity.
        """
        if not is_valid_date(date):
            await ctx.send("This is not a valid date! The date has to be DD/MM/YYYY, try again.")
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

    @commands.command(usage="!modifyactivity <activity_id> <date_or_time> (<time>)",
                      description="Modify an activity",
                      help="!modifyactivity 1 15/12/2024 (15:00)",
                      aliases=['ma', 'ea', 'editactivity'])
    async def modifyactivity(self, ctx: discord.ext.commands.context.Context, activity_id: int, date_or_time: str, p_time: str = None) -> None:
        """
        Modify an activity.

        :param ctx: The context.
        :param activity_id: The id of the activity.
        :param date_or_time: The date or time of the activity.
        """
        activities_obj: ActivitiesObj = load_activities_from_file(self.filename)

        if len(activities_obj.activities) == 0:
            await ctx.send("No activities planned!")
            return

        if activity_id < 1 or activity_id > len(activities_obj.activities):
            await ctx.send(f"The id must be greater than 0 and less than {len(activities_obj.activities) + 1}!")
            return

        if not is_valid_date(date_or_time) and not re.match("^(?:[01]\d|2[0-3]):[0-5]\d$", date_or_time):
            await ctx.send("This is not a valid date (DD/MM/YYYY) or time (HH:MM), try again!")
            return

        activity = activities_obj.activities[activity_id - 1]

        if is_valid_date(date_or_time):
            activity_date = string_to_date(date_or_time)
            if p_time is not None and not re.match("^(?:[01]\d|2[0-3]):[0-5]\d$", p_time):
                await ctx.send("Time has to be HH:MM, try again.")
                return
            elif p_time is not None:
                activity_time = string_to_time(p_time)
            else:
                activity_time = activity.time
        else:
            if re.match("^(?:[01]\d|2[0-3]):[0-5]\d$", date_or_time) and p_time is not None and is_valid_date(p_time):
                await ctx.send("Make sure the date comes before the time!")
                return
            activity_date = activity.date
            activity_time = string_to_time(date_or_time)

        if datetime.datetime.combine(activity_date, activity_time) <= datetime.datetime.now():
            await ctx.send("Unfortunately, we cannot go back to the past!")
            return

        activity.date, activity.time = activity_date, activity_time
        write_activities_to_file(self.filename, activities_obj)

        await ctx.send("Activity modified!")

    @commands.command(usage="!listactivities <activity_id>",
                      description="List all activities or one activity in particular",
                      help="!listactivities (1)",
                      aliases=['la'])
    async def listactivities(self, ctx: commands.Context, activity_id: int = None) -> None:
        """
        List all activities or one activity in particular.

        :param ctx: The context.
        :param activity_id: The id of the activity.
        """
        activities_obj: ActivitiesObj = load_activities_from_file(self.filename)

        if len(activities_obj.activities) == 0:
            await ctx.send("No activities planned!")

        messages = activities_obj.list_activities()

        if activity_id is not None and (activity_id < 1 or activity_id > len(activities_obj.activities)):
            await ctx.send(f"The id must be greater than 0 and less than {len(activities_obj.activities) + 1}!")
            return

        # list all activities or one in particular
        if activity_id is None:
            page = 0
            embed = discord.Embed(title=messages[0][0], description='\n'.join(list(map(lambda x: x[0] + f' ({x[1]} participants)' if x[1] != 1 else x[0] + ' (1 participant)', messages[0][1]))))
        else:
            page = len(messages) - 1 + activity_id
            activity = activities_obj.activities[activity_id - 1]
            embed = discord.Embed(title=f'{activity.name} ({convert_date_and_time_to_unix_time(datetime.datetime.combine(activity.date, activity.time))})', description=activities_obj.get_string_of_participants_of_activity(activity_id - 1))

        view = Menu(self.filename, messages, activities_obj, page=page)
        try:
            await ctx.send(embed=embed, view=view)
        except Exception as e:
            print(e)

    @commands.command(usage="!deleteactivity <activity_id>",
                      description="Delete an activity from the list of activities",
                      help="!deleteactivity 1",
                      aliases=['da'])
    async def deleteactivity(self, ctx: commands.Context, activity_id: int) -> None:
        """
        Remove an activity from the list.

        :param ctx: The context.
        :param activity_id: The id of the activity.
        """
        activities_obj: ActivitiesObj = load_activities_from_file(self.filename)

        if len(activities_obj.activities) == 0:
            await ctx.send("There are no activities planned!")

        if activity_id < 1 or activity_id > len(activities_obj.activities):
            await ctx.send(f"The id must be greater than 0 and less than {len(activities_obj.activities) + 1}!")
            return

        activities = load_activities_from_file(self.filename)
        message = activities.remove_activity(activity_id)
        write_activities_to_file(self.filename, activities)

        await ctx.send(message)


class Menu(discord.ui.View):
    """
    This class represents the view. It contains the filename in which the data is stored and the buttons.
    """
    def __init__(self, filename: str, activities_messages: List[Tuple[str, List[Tuple[str, int]]]], activities_obj: ActivitiesObj, page: int = 0):
        super().__init__()

        self.filename = filename
        self.activities_messages = activities_messages
        self.activities_obj = activities_obj

        if page == len(self.activities_messages) + len(self.activities_obj.activities) - 1:
            self.enable_and_disable_button('>', disabled=True)

        if page != 0:
            self.enable_and_disable_button('<')
            self.enable_and_disable_button('join')
            self.enable_and_disable_button('leave')

        self.page = page

    @discord.ui.button(label="<", style=discord.ButtonStyle.blurple, custom_id="<", disabled=True)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        Go to the previous tab and show its elements.

        :param interaction: Used to handle the button interaction.
        :param button: The button object.
        """
        self.activities_obj = load_activities_from_file(self.filename)

        self.activities_messages = self.activities_obj.list_activities()

        self.page = (self.page - 1) % (len(self.activities_obj.activities) + len(self.activities_messages))

        if self.page < len(self.activities_messages):
            self.enable_and_disable_button('join', disabled=True)
            self.enable_and_disable_button('leave', disabled=True)

        self.enable_and_disable_button('>')

        if self.page == 0:
            button.disabled = True
        else:
            button.disabled = False

        embed = await self.make_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Join", style=discord.ButtonStyle.green, custom_id="join", disabled=True)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        Join an activity.

        :param interaction: Used to handle the button interaction.
        :param button: The button object.
        """
        self.activities_obj = load_activities_from_file(self.filename)

        self.activities_messages = self.activities_obj.list_activities()

        activity_index = self.page - len(self.activities_messages)

        self.activities_obj.activities[activity_index].participating_individuals[interaction.user.id] = interaction.user.name

        page_index, activity_index_on_page = get_indices_of_activity(self.activities_messages, activity_index)

        self.activities_messages[page_index][1][activity_index_on_page] = (self.activities_messages[page_index][1][activity_index_on_page][0], len(self.activities_obj.activities[activity_index].participating_individuals))

        write_activities_to_file(self.filename, self.activities_obj)

        embed = await self.make_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Leave", style=discord.ButtonStyle.red, custom_id="leave", disabled=True)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        Leave an activity.

        :param interaction: Used to handle the button interaction.
        :param button: The button object.
        """
        self.activities_obj = load_activities_from_file(self.filename)

        self.activities_messages = self.activities_obj.list_activities()

        activity_index = self.page - len(self.activities_messages)

        participating_individuals = self.activities_obj.activities[activity_index].participating_individuals
        if interaction.user.id in participating_individuals:
            del participating_individuals[interaction.user.id]

        page_index, activity_index_on_page = get_indices_of_activity(self.activities_messages, activity_index)

        self.activities_messages[page_index][1][activity_index_on_page] = (self.activities_messages[page_index][1][activity_index_on_page][0], len(self.activities_obj.activities[activity_index].participating_individuals))

        write_activities_to_file(self.filename, self.activities_obj)

        embed = await self.make_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label=">", style=discord.ButtonStyle.blurple, custom_id=">")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        Go to the next tab and show its elements.

        :param interaction: Used to handle the button interaction.
        :param button: The button object.
        """
        self.activities_obj = load_activities_from_file(self.filename)

        self.activities_messages = self.activities_obj.list_activities()

        self.page = (self.page + 1) % (len(self.activities_obj.activities) + len(self.activities_messages))

        if self.page >= len(self.activities_messages):
            self.enable_and_disable_button('join')
            self.enable_and_disable_button('leave')

        self.enable_and_disable_button('<')

        if self.page == len(self.activities_obj.activities) + len(self.activities_messages) - 1:
            button.disabled = True
        else:
            button.disabled = False

        embed = await self.make_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="♻️", style=discord.ButtonStyle.blurple, custom_id="refresh")
    async def refresh(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        Refresh the current message.

        :param interaction: Used to handle the button interaction.
        :param button: The button object.
        """
        self.activities_obj = load_activities_from_file(self.filename)

        self.activities_messages = self.activities_obj.list_activities()

        embed = await self.make_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    def enable_and_disable_button(self, custom_id: str, disabled: bool = False) -> None:
        """
        Enable or disable the button with a certain custom id.

        :param custom_id: The custom id of the button to enable or disable.
        :param disabled: True if the button needs to be disabled, else False.
        """
        child_index = 0
        while child_index < len(self.children) and self.children[child_index].custom_id != custom_id:
            child_index += 1

        self.children[child_index].disabled = disabled

    async def make_embed(self) -> discord.embeds.Embed:
        """
        Create the views of the activities.

        :return: The embedded strings.
        """
        if self.page < len(self.activities_messages):
            return discord.Embed(title=self.activities_messages[self.page][0], description='\n'.join(list(map(lambda x: x[0] + f' ({x[1]} participants)' if x[1] != 1 else x[0] + ' (1 participant)', self.activities_messages[self.page][1]))))

        activity = self.activities_obj.activities[self.page - len(self.activities_messages)]
        name = activity.name

        return discord.Embed(title=f'{name} ({convert_date_and_time_to_unix_time(datetime.datetime.combine(activity.date, activity.time))})', description=self.activities_obj.get_string_of_participants_of_activity(self.page - len(self.activities_messages)))


# Allows to connect cog to bot
async def setup(client):
    await client.add_cog(Activities(client))
