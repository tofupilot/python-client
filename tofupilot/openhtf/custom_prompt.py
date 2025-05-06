"""Module for custom OpenHTF user prompt integration with TofuPilot."""

import logging
from typing import Text, Optional, Union, Callable

import openhtf
from openhtf import plugs
from openhtf.plugs.user_input import UserInput

_LOG = logging.getLogger(__name__)

def prompt_with_tofupilot_url(
    message: Text,
    operator_page_url: Optional[Text] = None,
    text_input: bool = False,
    timeout_s: Union[int, float, None] = None,
    cli_color: Text = '',
    image_url: Optional[Text] = None) -> Text:
    """Enhanced prompt that displays TofuPilot URL in the console.
    
    Args:
      message: A string to be presented to the user.
      operator_page_url: URL to the TofuPilot operator page.
      text_input: A boolean indicating whether the user must respond with text.
      timeout_s: Seconds to wait before raising a PromptUnansweredError.
      cli_color: An ANSI color code, or the empty string.
      image_url: Optional image URL to display or None.
      
    Returns:
      A string response, or the empty string if text_input was False.
    """
    # Get the UserInput plug instance
    prompts = plugs.get_plug_instance(UserInput)
    
    # Log the operator page URL to the console with clean formatting
    if operator_page_url:
        print(f"\n📱 View live test results: {operator_page_url}")
    
    # Use the standard prompt method with original message
    return prompts.prompt(
        message, 
        text_input=text_input,
        timeout_s=timeout_s, 
        cli_color=cli_color, 
        image_url=image_url
    )


def enhanced_prompt_for_test_start(
    operator_page_url: Optional[Text] = None,
    message: Text = 'Enter a DUT ID in order to start the test.',
    timeout_s: Union[int, float, None] = 60 * 60 * 24,
    validator: Callable[[Text], Text] = lambda sn: sn,
    cli_color: Text = '') -> openhtf.PhaseDescriptor:
    """Returns an OpenHTF phase that displays TofuPilot URL in the console.
    
    Args:
      operator_page_url: URL to the TofuPilot operator page.
      message: The message to display to the user.
      timeout_s: Seconds to wait before raising a PromptUnansweredError.
      validator: Function used to validate or modify the serial number.
      cli_color: An ANSI color code, or the empty string.
    """
    
    @openhtf.PhaseOptions(timeout_s=timeout_s)
    @plugs.plug(prompts=UserInput)
    def trigger_phase(test: openhtf.TestApi, prompts: UserInput) -> None:
        """Test start trigger with TofuPilot URL displayed in console."""
        # Log the operator page URL to the console
        if operator_page_url:
            print(f"\n📱 View live test results: {operator_page_url}")
        
        # Standard OpenHTF prompt
        dut_id = prompts.prompt(
            message,
            text_input=True, 
            timeout_s=timeout_s, 
            cli_color=cli_color
        )
        
        # Apply validator and set DUT ID
        test.test_record.dut_id = validator(dut_id)
    
    return trigger_phase


# Monkey-patching function to include TofuPilot URL in prompts
original_prompt = UserInput.prompt

def patched_prompt(self, message, text_input=False, timeout_s=None, cli_color='', image_url=None, 
                  tofupilot_url=None):
    """Patched prompt method that displays TofuPilot URL in console."""
    # Display TofuPilot URL if available
    if tofupilot_url:
        print(f"\n📱 View live test results: {tofupilot_url}")
    
    # Call the original prompt method
    return original_prompt(self, message, text_input, timeout_s, cli_color, image_url)


def patch_openhtf_prompts(tofupilot_url=None):
    """Monkey-patch OpenHTF's UserInput class to display TofuPilot URL.
    
    This function should be called early in your application to ensure all prompts
    show the TofuPilot URL in the console (not in the prompt text itself).
    
    Args:
        tofupilot_url: URL to the TofuPilot operator page.
    """
    if tofupilot_url:
        # Store URL in UserInput class for access by all instances
        UserInput.tofupilot_url = tofupilot_url
        
        # Monkey-patch the prompt method
        UserInput.prompt = lambda self, message, text_input=False, timeout_s=None, cli_color='', image_url=None: \
            patched_prompt(self, message, text_input, timeout_s, cli_color, image_url, tofupilot_url)
        
        _LOG.info(f"Enhanced OpenHTF prompts with TofuPilot URL: {tofupilot_url}")
    else:
        _LOG.warning("No TofuPilot URL provided for prompt enhancement")