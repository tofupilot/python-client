import openhtf
from openhtf import plugs
from openhtf.core.base_plugs import FrontendAwareBasePlug
from openhtf.plugs.user_input import PromptUnansweredError

import threading
import base64
import uuid
import json
import time
from typing import Any, Callable, Dict, Optional, Union, Literal
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from typing import Union, Tuple

def _validate_id(id: Optional[str]) -> str:
    if id == '':
        raise ValueError("id cannot be the empty string")
    
    if id == None:
        return ''
    else:
        return id

@dataclass(frozen=True)
class Element(ABC):
    @abstractmethod
    def _as_static(self) -> "StaticElement":
        raise NotImplementedError(f"{self.__class__.__name__} does not implement `_as_sendable`")

@dataclass(frozen=True)
class StaticElement(Element):

    def _as_static(self):
        return self

    def _asdict(self):
        return {
            "class": self.__class__.__name__,
            **asdict(self),
        }

# Output

@dataclass(frozen=True)
class Text(StaticElement):
    s: str

@dataclass(frozen=True)
class Base64Image(StaticElement):
    data: str

# Input

@dataclass(frozen=True)
class FormInput(StaticElement):
    """
    Abstract, should not be directy instantiated!

    Parent class of all form-only inputs

    Provides an identifier to be used to retrieve the value
    """
    id: str

@dataclass(frozen=True)
class TextInput(FormInput):
    placeholder: Optional[str]

@dataclass(frozen=True)
class Select(FormInput):
    choices: Tuple[str, ...]

# Layout

## Static

@dataclass(frozen=True)
class StaticFlex(StaticElement):
    children: Tuple['StaticElement', ...]
    direction: Literal['top_down', 'bottom_up', 'left_to_right', 'right_to_left']

    def _asdict(self):
        children_dicts = tuple(map(lambda c: c._asdict(), self.children))
        return { "class": "Flex", "direction": self.direction, "children": children_dicts}

## Potentially dynamic

@dataclass(frozen=True)
class Flex(Element):
    children: Tuple['Element', ...]
    direction: Literal['top_down', 'bottom_up', 'left_to_right', 'right_to_left']

    def _as_static(self):
        static_children = tuple(map(lambda c: c._as_static(), self.children))
        return StaticFlex(children=static_children, direction=self.direction)

# Dynamic

@dataclass(frozen=True)
class Dynamic(Element):
    child: Callable[[], Element]

    def _as_static(self):
        return self.child()._as_static()

def _parse_children(children: Tuple[Union[str, Element, None], ...]) -> Tuple[Element, ...]:
    """
    Remove `None`s and convert `str` to `Text` elements
    """

    return tuple(
        map(
            lambda c: Text(c) if isinstance(c, str) else c,
            filter(lambda c: c != None, children)
        )
    )

@dataclass()
class Prompt:
    id: str
    element: Element
    update_period: float
    _previous_element: Optional[StaticElement] = None
    _previous_element_expiry_time: float = 0

    def _asdict(self) -> Dict[str, Any]:
        current_time = time.time()
        if self._previous_element is None or current_time > self._previous_element_expiry_time:
            self._previous_element = self.element._as_static()
            self._previous_element_expiry_time = current_time + self.update_period

        return {
            'id': self.id,
            'element': self._previous_element._asdict(),
        }

# Outputs

def text(s: str) -> Text:
    "Text to be displayed to the user, python `str` can also be used"
    return Text(s=s)

def image(*, path: str) -> Base64Image:
    "Image to be displayed to the user"
    with open(path, "rb") as file:
        # Encode the file to base 64 (b64encode), then convert to a string (decode)
        return Base64Image(data=base64.b64encode(file.read()).decode())

# Inputs

def text_input(placeholder: Union[str, None] = None, *, id: Optional[str] = None) -> TextInput:
    "A place for the user to input text"
    return TextInput(placeholder=placeholder, id=_validate_id(id))

def select(*choices: str, id: Optional[str] = None) -> Select:
    return Select(choices=choices, id=_validate_id(id))

# Layout

def top_down(*children: Union[str, Element, None]) -> Flex:
    return Flex(children=_parse_children(children), direction='top_down')

def left_to_right(*children: Union[str, Element, None]) -> Flex:
    return Flex(children=_parse_children(children), direction='left_to_right')

# Dynamic

def dynamic(child: Callable[[], Element]) -> Dynamic:
    return Dynamic(child=child)

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
        """Return a dictionary representation of the current state."""
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
                element,
                update_period=1,
            )
            self._previous_element = None

            self.notify_update()
            return prompt_id

    def wait_for_prompt(self, timeout_s: Union[int, float, None] = None) -> str:
        with self._cond:
            if self._prompt:
                # if timeout_s is none, wait forever
                self._cond.wait(timeout_s)
            if self._response is None:
              raise PromptUnansweredError
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
            parsed = json.loads(response)

            # Shortcut: If the user defined only one input with no id, 
            #   return that single value instead of the dict
            no_id = ''
            if len(parsed) == 1 and no_id in parsed.keys():
                self._response = parsed[no_id]
            else:
                self._response = parsed
            
            self.last_response = (prompt_id, response)
            self.remove_prompt()
            self._cond.notify_all()


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

    @openhtf.PhaseOptions(timeout_s=timeout_s)
    @plugs.plug(ui_plug=OperatorUiPlug)
    def trigger_phase(test: openhtf.TestApi, ui_plug: OperatorUiPlug) -> None:
        """Test start trigger that prompts the user for a DUT ID."""
        dut_id = ui_plug.prompt(
            top_down(
                message,
                text_input(),
            ),
            timeout_s=timeout_s,
        )
        test.test_record.dut_id = validator(dut_id)

    return trigger_phase
