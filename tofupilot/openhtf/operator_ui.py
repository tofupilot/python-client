from openhtf.core.base_plugs import FrontendAwareBasePlug

import functools
import logging
import os
import platform
import select
import sys
import threading
from typing import Any, Callable, Dict, Optional, Union
import uuid
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Union, Tuple

import attr

@dataclass
class Element(ABC):
    @abstractmethod
    def as_dict(self):
        pass

@dataclass
class Text(Element):
    s: str

    def as_dict(self):
        return { "class": "Text", "s": self.s}
    
@dataclass
class TextInput(Element):
    placeholder: Optional[str]

    def as_dict(self):
        return { "class": "TextInput", "s": self.placeholder}

@dataclass
class Select(Element):
    choices: Tuple[str, ...]

    def as_dict(self):
        return { "class": "Select", "choices": self.choices}

@dataclass  
class TopDown(Element):
    children: Tuple['Element', ...]

    def as_dict(self):
        print(self.children)
        children_dicts = tuple(map(lambda c: c.as_dict(), self.children))
        return { "class": "TopDown", "options": children_dicts}

@attr.s(slots=True, frozen=True)
class Prompt(object):
    id = attr.ib(type=Text)
    message = attr.ib(type=Text)
    text_input = attr.ib(type=bool)
    image_url = attr.ib(type=Optional[Text], default=None)

class OperatorUiPlug(FrontendAwareBasePlug):
    """Get user input from inside test phases.

    Attributes:
        last_response: None, or a pair of (prompt_id, response) indicating the last
        user response that was received by the plug.
    """

    def __init__(self):
        super(OperatorUiPlug, self).__init__()
        self.last_response: Optional[tuple[str, str]] = None
        self._prompt: Optional[Prompt] = None
        #self._console_prompt: Optional[ConsolePrompt] = None
        self._response: Optional[str] = None
        self._cond = threading.Condition(threading.RLock())

    def _asdict(self) -> Optional[Dict[str, Any]]:
        """Return a dictionary representation of the current prompt."""
        with self._cond:
            if self._prompt is None:
                return None
            return {
                'id': self._prompt.id,
                'message': self._prompt.message,
                'text-input': self._prompt.text_input,
                'image-url': self._prompt.image_url
            }

    def tearDown(self) -> None:
        self.remove_prompt()

    def remove_prompt(self) -> None:
        """Remove the prompt."""
        with self._cond:
            self._prompt = None
            #if self._console_prompt:
            #  self._console_prompt.stop()
            #  self._console_prompt = None
            self.notify_update()

    def prompt(self,
                message: Text,
                text_input: bool = False,
                timeout_s: Union[int, float, None] = None,
                cli_color: Text = '',
                image_url: Optional[Text] = None) -> Text:
        """Display a prompt and wait for a response.

        Args:
        message: A string to be presented to the user.
        text_input: A boolean indicating whether the user must respond with text.
        timeout_s: Seconds to wait before raising a PromptUnansweredError.
        cli_color: An ANSI color code, or the empty string.
        image_url: Optional image URL to display or None.

        Returns:
        A string response, or the empty string if text_input was False.

        Raises:
        MultiplePromptsError: There was already an existing prompt.
        PromptUnansweredError: Timed out waiting for the user to respond.
        """
        self.start_prompt(message, text_input, cli_color, image_url)
        return self.wait_for_prompt(timeout_s)

    def start_prompt(self,
                    message: Text,
                    text_input: bool = False,
                    cli_color: Text = '',
                    image_url: Optional[Text] = None) -> Text:
        """Display a prompt.

        Args:
        message: A string to be presented to the user.
        text_input: A boolean indicating whether the user must respond with text.
        cli_color: An ANSI color code, or the empty string.
        image_url: Optional image URL to display or None.

        Raises:
        MultiplePromptsError: There was already an existing prompt.

        Returns:
        A string uniquely identifying the prompt.
        """
        with self._cond:
            #if self._prompt:
            #  raise MultiplePromptsError(
            #      'Multiple concurrent prompts are not supported.')
            prompt_id = uuid.uuid4().hex

            self._response = None
            self._prompt = Prompt(
                id=prompt_id,
                message=message,
                text_input=text_input,
                image_url=image_url)
            #if sys.stdin.isatty():
                #self._console_prompt = ConsolePrompt(message, functools.partial(self.respond, prompt_id), cli_color)
                #self._console_prompt.start()

            self.notify_update()
            return prompt_id

    def wait_for_prompt(self, timeout_s: Union[int, float, None] = None) -> str:
        """Wait for the user to respond to the current prompt.

        Args:
        timeout_s: Seconds to wait before raising a PromptUnansweredError.

        Returns:
        A string response, or the empty string if text_input was False.

        Raises:
        PromptUnansweredError: Timed out waiting for the user to respond.
        """
        with self._cond:
            if self._prompt:
                if timeout_s is None:
                    self._cond.wait(3600 * 24 * 365)
                else:
                    self._cond.wait(timeout_s)
            #if self._response is None:
            #  raise PromptUnansweredError
            return self._response

    def respond(self, prompt_id: str, response: str) -> None:
        """Respond to the prompt with the given ID.

        If there is no active prompt or the given ID doesn't match the active
        prompt, do nothing.

        Args:
        prompt_id: A string uniquely identifying the prompt.
        response: A string response to the given prompt.
        """
        #_LOG.debug('Responding to prompt (%s): "%s"', prompt_id, response)
        with self._cond:
            if not (self._prompt and self._prompt.id == prompt_id):
                return
            self._response = response
            self.last_response = (prompt_id, response)
            self.remove_prompt()
            self._cond.notifyAll()

    # TODO: Reimplement this with new framework
    """
    def prompt_for_test_start(
        message: str = 'Enter a DUT ID in order to start the test.',
        timeout_s: Union[int, float, None] = 60 * 60 * 24,
        validator: Callable[[str], str] = lambda sn: sn,
        cli_color: str = '') -> openhtf.PhaseDescriptor:
        ""Returns an OpenHTF phase for use as a prompt-based start trigger.

        Args:
            message: The message to display to the user.
            timeout_s: Seconds to wait before raising a PromptUnansweredError.
            validator: Function used to validate or modify the serial number.
            cli_color: An ANSI color code, or the empty string.
        ""

        @openhtf.PhaseOptions(timeout_s=timeout_s)
        @plugs.plug(prompts=UserInput)
        def trigger_phase(test: openhtf.TestApi, prompts: UserInput) -> None:
            ""Test start trigger that prompts the user for a DUT ID.""
            dut_id = prompts.prompt(
                message, text_input=True, timeout_s=timeout_s, cli_color=cli_color)
            test.test_record.dut_id = validator(dut_id)

        return trigger_phase
    """

class OperatorUi:
    plug = OperatorUiPlug

    def text(s: str) -> Text:
        "Text to be displayed to the user, python `str` can also be used"
        return Text(s)
    
    def text_input(placeholder: str = None) -> TextInput:
        "A place for the user to input text"
        return TextInput(placeholder)
    
    def select(*choices: str) -> Select:
        return Select(choices)
    
    def top_down(*children: Union[str, Element]) -> TopDown:
        elements: tuple[Element] = tuple(map(lambda c: Text(c) if isinstance(c, str) else c, children))
        return TopDown(elements)
