import openhtf
from openhtf import plugs
from openhtf.core.base_plugs import FrontendAwareBasePlug

import threading
from typing import Any, Callable, Dict, Optional, Union
import uuid
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from typing import Union, Tuple

@dataclass(frozen=True)
class Element(ABC):

    def _asdict(self):
        return {
            "class": self.__class__.__name__,
            **asdict(self),
        }

# Output

@dataclass(frozen=True)
class Text(Element):
    s: str

@dataclass(frozen=True)
class Base64Image(Element):
    data: str

# Input

@dataclass(frozen=True)
class TextInput(Element):
    placeholder: Optional[str]
    id: Union[str, None] = None

@dataclass(frozen=True)
class Select(Element):
    choices: Tuple[str, ...]
    id: Union[str, None] = None

# Layout

@dataclass(frozen=True)
class TopDown(Element):
    children: Tuple['Element', ...]

    def _asdict(self):
        children_dicts = tuple(map(lambda c: c._asdict(), self.children))
        return { "class": "TopDown", "children": children_dicts}

@dataclass(frozen=True)
class Prompt:
    id: str
    element: Element

    def _asdict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'element': self.element._asdict(),
        }

class OperatorUiPlug(FrontendAwareBasePlug):
    """Get user input from inside test phases.

    Attributes:
        last_response: None, or a pair of (prompt_id, response) indicating the last
        user response that was received by the plug.
    """

    def __init__(self):
        super(OperatorUiPlug, self).__init__()
        # TODO: Remove last_response
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
            return self._prompt._asdict()

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

    def prompt(self, element: Element, *, timeout_s: Union[int, float, None] = None) -> str:
        self.start_prompt(element)
        return self.wait_for_prompt(timeout_s)

    def start_prompt(self, element: Element) -> str:
        with self._cond:
            #if self._prompt:
            #  raise MultiplePromptsError(
            #      'Multiple concurrent prompts are not supported.')
            prompt_id = uuid.uuid4().hex

            self._response = None
            self._prompt = Prompt(
                prompt_id,
                element
            )

            self.notify_update()
            return prompt_id

    def wait_for_prompt(self, timeout_s: Union[int, float, None] = None) -> str:
        with self._cond:
            if self._prompt:
                # if timeout_s is none, wait forever
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
        response: The response to the given prompt.
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

class OperatorUi:
    plug = OperatorUiPlug

    # Outputs

    def text(s: str) -> Text:
        "Text to be displayed to the user, python `str` can also be used"
        return Text(s)
    
    def image(*, path: str) -> Base64Image:
        "Image to be displayed to the user"
        with open(path, "rb") as file:
            # Encode the file to base 64 (b64encode), then convert to a string (decode)
            return Base64Image(base64.b64encode(file.read()).decode())
    
    # Inputs

    def text_input(placeholder: str = None, *, id: Optional[str] = None) -> TextInput:
        "A place for the user to input text"
        return TextInput(placeholder, id)
    
    def select(*choices: str, id: Optional[str] = None) -> Select:
        return Select(choices, id)
    
    # Layout
    
    def top_down(*children: Union[str, Element, None]) -> TopDown:
        
        # Remove `None`s and convert `str` to `Text` elements
        elements: tuple[Element] = tuple(
            map(
                lambda c: Text(c) if isinstance(c, str) else c,
                filter(lambda c: c != None, children)
            )
        )
        return TopDown(elements)
    
def prompt_for_test_start(
    message: str = 'Enter a DUT ID in order to start the test.',
    timeout_s: Union[int, float, None] = 60 * 60 * 24,
    validator: Callable[[str], str] = lambda sn: sn,
    ) -> openhtf.PhaseDescriptor:
    """Returns an OpenHTF phase for use as a prompt-based start trigger.

    Drop-in replacement for openhtf.plugs.user_input.prompt_for_test_start.
    (If you were using cli_color, remove that parameter)

    Args:
        message: The message to display to the user.
        timeout_s: Seconds to wait before raising a PromptUnansweredError.
        validator: Function used to validate or modify the serial number.
    """
    ui = OperatorUi

    @openhtf.PhaseOptions(timeout_s=timeout_s)
    @plugs.plug(ui_plug=OperatorUi.plug)
    def trigger_phase(test: openhtf.TestApi, ui_plug: OperatorUi.plug) -> None:
        """Test start trigger that prompts the user for a DUT ID."""
        dut_id = ui_plug.prompt(
            ui.top_down(
                message,
                ui.text_input(),
            ),
            timeout_s=timeout_s,
        )
        test.test_record.dut_id = validator(dut_id)

    return trigger_phase
