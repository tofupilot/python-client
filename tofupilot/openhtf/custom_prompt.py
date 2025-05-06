"""Custom OpenHTF prompt integration with TofuPilot.

Enhances OpenHTF prompts with TofuPilot features:
- Clickable URLs in the console
- Bold question text
- Consistent visual formatting
- Compatible with TofuPilot web UI streaming

Prompt format:
- [User Input] QUESTION TEXT (bold)
- Waiting for user input on TofuPilot Operator UI (clickable) or in terminal below.
- Press Ctrl+C to cancel and upload results. (muted)
- Standard OpenHTF prompt (-->)

Note: The message appears twice in the console to ensure web UI compatibility.
"""

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
    import sys
    
    # Get the UserInput plug instance
    prompts = plugs.get_plug_instance(UserInput)
    
    # Print URL and instructions directly to console before the prompt
    # This way they won't appear in the web UI
    if operator_page_url:
        # Create clickable URL if in terminal that supports it
        try:
            # Create clickable URL with ANSI escape sequences
            # Make both "TofuPilot Operator UI" clickable
            clickable_text = f"\033]8;;{operator_page_url}\033\\TofuPilot Operator UI\033]8;;\033\\"
            sys.stdout.write(f"\n[User Input] \033[1m{message}\033[0m\n")
            sys.stdout.write(f"Waiting for user input on {clickable_text} or in terminal below.\n")
            # sys.stdout.write("\033[2mPress Ctrl+C to cancel and upload results.\033[0m\n\n")
            sys.stdout.flush()
        except:
            # Fallback if terminal doesn't support ANSI sequences
            print(f"\n[User Input] {message}")
            print(f"Waiting for user input on TofuPilot Operator UI or in terminal below.")
            # print("Press Ctrl+C to cancel and upload results.\n")
    
    # Store original message and use it for web UI compatibility
    original_msg = message
    
    # Use dim/muted text for the prompt
    if not cli_color:
        cli_color = '\033[2m'
    return prompts.prompt(
        original_msg, 
        text_input=text_input,
        timeout_s=timeout_s, 
        cli_color=cli_color, 
        image_url=image_url
    )


def enhanced_prompt_for_test_start(
    operator_page_url: Optional[Text] = None,
    message: Text = 'Enter a DUT ID in order to start the test.',
    timeout_s: Union[int, float, None] = 60 * 60 * 24,
    validator: Callable[[Text], Text] = lambda sn: sn) -> openhtf.PhaseDescriptor:
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
        import sys
        
        # Print URL and instructions directly to console before the prompt
        # This way they won't appear in the web UI
        if operator_page_url:
            # Create clickable URL if in terminal that supports it
            try:
                # Create clickable URL with ANSI escape sequences
                # Make both "TofuPilot Operator UI" clickable
                clickable_text = f"\033]8;;{operator_page_url}\033\\TofuPilot Operator UI\033]8;;\033\\"
                sys.stdout.write(f"\n[User Input] \033[1m{message}\033[0m\n")
                sys.stdout.write(f"Waiting for user input on {clickable_text} or in terminal below.\n")
                sys.stdout.write("\033[2mPress Ctrl+C to cancel and upload results.\033[0m\n\n")
                sys.stdout.flush()
            except:
                # Fallback if terminal doesn't support ANSI sequences
                print(f"\n[User Input] {message}")
                print(f"Waiting for user input on TofuPilot Operator UI or in terminal below.")
                # print("Press Ctrl+C to cancel and upload results.\n")
        
        # Store original message and use it for web UI compatibility
        original_msg = message
        
        # Use dim/muted text for the prompt
        if not cli_color:
            cli_color = '\033[2m'
        dut_id = prompts.prompt(
            original_msg,
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
    import sys
    
    # Store original message to use in web UI
    original_msg = message
    
    # Print URL and instructions directly to console before the prompt
    # This way they won't appear in the web UI
    if tofupilot_url:
        # Create clickable URL if in terminal that supports it
        try:
            # Create clickable URL with ANSI escape sequences
            # Make both "TofuPilot Operator UI" clickable
            clickable_text = f"\033]8;;{tofupilot_url}\033\\TofuPilot Operator UI\033]8;;\033\\"
            sys.stdout.write(f"\n[User Input] \033[1m{message}\033[0m\n")
            sys.stdout.write(f"Waiting for user input on {clickable_text} or in terminal below.\n")
            # sys.stdout.write("\033[2mPress Ctrl+C to stop and upload run.\033[0m\n\n")
            sys.stdout.flush()
            
        except:
            # Fallback if terminal doesn't support ANSI sequences
            print(f"\n[User Input] {message}")
            print(f"Waiting for user input on TofuPilot Operator UI or in terminal below.")
            # print("Press Ctrl+C to cancel and upload results.\n")
    
    # Override cli_color to make the OpenHTF prompt appear dimmed
    # This works because the cli_color is applied to the prompt arrow
    if not cli_color:
        cli_color = '\033[2m'  # Use dim/muted text if no color specified
    
    # Use original message for web UI compatibility
    return original_prompt(self, original_msg, text_input, timeout_s, cli_color, image_url)


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
    else:
        _LOG.debug("No TofuPilot URL provided for prompt enhancement")