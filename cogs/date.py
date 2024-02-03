import datetime
import os
import pickle
import re
from typing import List, Tuple

import discord
from discord.ext import commands, tasks

utc = datetime.timezone.utc


class Exam:
    def __init__(self, date: datetime.date, name: str, person_id: int, person_name: str):
        self.date = date
        self.name = name
        self.person_id = person_id
        self.person_name = person_name

    def get_string_representation(self) -> str:
        """
        Obtain the string representation of an exam.

        :return: The string representation.
        """
        return f'{self.person_name} heeft examen {self.name}.'

    def __lt__(self, other) -> bool:
        """
        Override the less than operator so that you can sort a list of exams.

        :param other: The other Exam object.

        :return: True if the object is smaller than the other one, else False.
        """
        if self.date != other.date:
            return self.date < other.date

        if self.person_name != other.person_name:
            return self.person_name < other.person_name

        if self.name != other.name:
            return self.name < other.name

        return self.person_id < other.person_id

    def __eq__(self, other) -> bool:
        """
        Override the __eq__ operator so that you can sort a list of exams.

        :param other: The other Exam object.

        :return: True if the objects are equal, else False.
        """
        return self.date == other.date and self.person_id == other.person_id and self.name == other.name


class ExamsObj:
    """
    This class contains a list of Exam objects.
    """
    def __init__(self):
        self.exams: List[Exam] = []

    def add_exam(self, new_exam: Exam):
        """
        Add an exam to the list of exams if it doesn't exist yet.

        :param new_exam: The new exam object.

        :return: The status message.
        """
        for index, exam in enumerate(self.exams):
            if new_exam == exam:
                return "This exam already exists!"

            if new_exam < exam:
                self.exams.insert(index, new_exam)
                return "Exam added!"

        self.exams.append(new_exam)

        return "Exam added!"

    def remove_exams_from_the_past(self) -> None:
        """
        Remove all outdated exams.
        """
        index = 0

        while index < len(self.exams) and self.exams[index].date < (datetime.datetime.now() - datetime.timedelta(days=1)).date():
            index += 1

        self.exams = self.exams[index:]

    def remove_exam(self, exam: Exam) -> str:
        """
        Remove an exam.

        :param exam: The exam object to delete.

        :return: The status message.
        """
        number_of_exams = len(self.exams)

        # filter the list of exams
        self.exams = list(filter(lambda x: x != exam, self.exams))

        if len(self.exams) != number_of_exams:
            return "Exam deleted!"

        return "This exam doesn't exist!"

    def list_exams(self) -> List[Tuple[str, str]]:
        """
        Obtain a list of pages/messages. Each page/message contains a title and a string of exams.

        :return: The list of pages/messages.
        """
        messages = []

        current_exam = self.exams[0]
        current_date = current_exam.date
        current_date_string = current_date.strftime("%d/%m/%Y")

        # start of first message
        message = [f"**__{current_date_string}:__**\n{current_exam.get_string_representation()}"]
        message_length = len(message[0][0])

        page = 1

        for current_exam in self.exams[1:]:
            # if message too large -> output
            if message_length > 750:
                messages.append((f'Exam dates {page}', '\n'.join(message)))

                page += 1

                # update the current date to sort the exams
                if current_exam.date != current_date:
                    current_date = current_exam.date
                    current_date_string = current_date.strftime("%d/%m/%Y")

                message = [f"\n**__{current_date_string}:__**\n{current_exam.get_string_representation()}"]
                message_length = len(message[0][0])
            elif current_exam.date != current_date:
                current_date = current_exam.date
                current_date_string = current_date.strftime("%d/%m/%Y")

                message_representation = f"\n**__{current_date_string}:__**\n{current_exam.get_string_representation()}"
                message_length += len(message_representation)
                message.append(message_representation)
            else:
                message_representation = current_exam.get_string_representation()
                message_length += len(message_representation)
                message.append(message_representation)

        if message_length > 0:
            messages.append((f'Exam dates {page}', '\n'.join(message)))

        return messages


def write_exam_dates_to_file(output_file: str, exams_obj: ExamsObj) -> None:
    """
    Write an Exams object to a pickle file.

    :param output_file: The output file.
    :param exams_obj: The exams object.
    """
    with open(output_file, 'wb') as file:
        pickle.dump(exams_obj, file)


def load_exams_from_file(input_file: str) -> ExamsObj:
    """
    Read an Exams object from a pickle file.

    :param input_file: The input file.

    :return: The Exams object.
    """
    with open(input_file, 'rb') as file:
        exams_obj = pickle.load(file)

    return exams_obj


def string_to_date(date_string: str) -> datetime.date:
    """
    Convert a string "day/month/year" to a date object.

    :param date_string: The date.

    :return: The date object.
    """
    return datetime.datetime.strptime(date_string, "%d/%m/%Y").date()


def is_valid_date(date_string):
    """
    Check if the provided date is valid.

    :param date_string: The date.

    :return: True if it is a valid date, else False.
    """
    try:
        datetime_object = datetime.datetime.strptime(date_string, '%d/%m/%Y')
        return True
    except ValueError:
        return False


class Exams(commands.Cog):
    """
    This class contains the filename in which the data is stored and the commands.
    """
    def __init__(self, client: discord.Client):
        self.client = client
        self.filename = 'exam_dates.pkl'
        self.check_loop.start()

    @tasks.loop(time=datetime.time(hour=23, minute=00, tzinfo=utc))
    async def check_loop(self) -> None:
        """
        Each day, remove all outdated activities at a certain time.
        """
        exams_obj = load_exams_from_file(self.filename)
        exams_obj.remove_exams_from_the_past()
        write_exam_dates_to_file(self.filename, exams_obj)

    @check_loop.before_loop
    async def before_printer(self):
        await self.client.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        Create the file in which the data will be stored.
        """
        if not os.path.exists(self.filename):
            write_exam_dates_to_file(self.filename, ExamsObj())
            print(f"{self.filename} created")

    @commands.command(usage="!adddate <date> <name>",
                      description="Add date to the list of exams",
                      help="!adddate 15/02/2022 a very hard exam\nDate should follow the format **DD/MM/YYYY**\nExam is allowed to contain **spaces**",
                      aliases=['ad'])
    async def adddate(self, ctx: commands.Context, date: str, *, name: str) -> None:
        """
        Add an exam to the list.

        :param ctx: The context.
        :param date: The date of the exam.
        :param name: The name of the exam.
        """
        if not is_valid_date(date):
            await ctx.send("This is not a valid date! The date has to be DD/MM/YYYY, try again.")
            return

        exam_date = string_to_date(date)

        if exam_date < datetime.datetime.now().date():
            await ctx.send("Unfortunately, we cannot go back to the past!")
            return

        exams = load_exams_from_file(self.filename)
        message = exams.add_exam(Exam(exam_date, name, ctx.message.author.id, ctx.message.author.name))
        write_exam_dates_to_file(self.filename, exams)

        await ctx.send(message)

    @commands.command(usage="!showdate <member>",
                      description="Show current examdates",
                      help="!showdate: Show all dates\n!showdate @member: Show all dates from certain member",
                      aliases=['sd'])
    async def showdate(self, ctx: commands.Context, member: discord.Member = None):
        """
        List all exams or the exams of one person in particular.

        :param ctx: The context.
        :param member: The member whose exams are being requested.
        """
        exams_obj = load_exams_from_file(self.filename)

        if len(exams_obj.exams) == 0:
            await ctx.send(f"No exams, hooray!!!")

        if member is not None:
            exams_obj.exams = list(filter(lambda exam: exam.person_id == member.id, exams_obj.exams))

        if len(exams_obj.exams) == 0:
            await ctx.send(f"{member.name} has no exams!")

        messages = exams_obj.list_exams()

        # list all exams or the exams of one person in particular
        embed = discord.Embed(title=messages[0][0], description=messages[0][1])

        view = Menu(self.filename, messages)
        try:
            await ctx.send(embed=embed, view=view)
        except Exception as e:
            print(e)

    @commands.command(usage="!deletedate <date> <name>",
                      description="Delete date from list of exams",
                      help="!deletedate 15/02/2022 a very hard exam\nThe arguments have to be **the same arguments** as the ones in !adddate",
                      aliases=['dd'])
    async def deletedate(self, ctx: commands.Context, date: str, *, name: str) -> None:
        """
        Remove an exam from the list.

        :param ctx: The context.
        :param date: The date of the exam.
        :param name: The name of the exam.
        """
        if not is_valid_date(date):
            await ctx.send("This is not a valid date! The date has to be DD/MM/YYYY, try again.")
            return

        exam_date = string_to_date(date)

        exams_obj: ExamsObj = load_exams_from_file(self.filename)

        if len(exams_obj.exams) == 0:
            await ctx.send("There are no exams!")

        message = exams_obj.remove_exam(Exam(exam_date, name, ctx.message.author.id, ctx.message.author.name))
        write_exam_dates_to_file(self.filename, exams_obj)

        await ctx.send(message)


class Menu(discord.ui.View):
    """
    This class represents the view. It contains the filename in which the data is stored and the buttons.
    """
    def __init__(self, filename: str, exam_messages: List[Tuple[str, str]]):
        super().__init__()

        self.filename = filename
        self.exam_messages = exam_messages

        if len(exam_messages) == 1:
            self.enable_and_disable_button('>', disabled=True)

        self.page = 0

    @discord.ui.button(label="<", style=discord.ButtonStyle.blurple, custom_id="<", disabled=True)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        Go to the previous tab and show its elements.

        :param interaction: Used to handle the button interaction.
        :param button: The button object.
        """
        self.page = (self.page - 1) % len(self.exam_messages)

        self.enable_and_disable_button('>')

        if self.page == 0:
            button.disabled = True
        else:
            button.disabled = False

        embed = await self.make_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label=">", style=discord.ButtonStyle.blurple, custom_id=">")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        Go to the next tab and show its elements.

        :param interaction: Used to handle the button interaction.
        :param button: The button object.
        """
        self.page = (self.page + 1) % len(self.exam_messages)

        self.enable_and_disable_button('<')

        if self.page == len(self.exam_messages) - 1:
            button.disabled = True
        else:
            button.disabled = False

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
        Create the views of the exams.

        :return: The embedded strings.
        """
        return discord.Embed(title=self.exam_messages[self.page][0], description=self.exam_messages[self.page][1])


# Allows to connect cog to bot
async def setup(client):
    await client.add_cog(Exams(client))
