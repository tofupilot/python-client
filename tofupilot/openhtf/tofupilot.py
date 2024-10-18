import os
from typing import Optional
from time import sleep
import threading
import asyncio

from openhtf import Test
from openhtf.util import data
from y_py import YDoc
from ypy_websocket import WebsocketProvider
from websockets import connect

from .upload import upload


def _get_executing_test():
    """Get the currently executing test and its state."""
    tests = list(Test.TEST_INSTANCES.values())

    if not tests:
        return None, None

    if len(tests) > 1:
        pass

    test = tests[0]
    test_state = test.state

    if test_state is None:
        return None, None

    return test, test_state


def _to_dict_with_event(test_state):
    """Process a test state into the format we want to send to the frontend."""
    original_dict, event = test_state.asdict_with_event()

    # This line may produce a 'dictionary changed size during iteration' error.
    test_state_dict = data.convert_to_base_types(original_dict)

    test_state_dict["execution_uid"] = test_state.execution_uid
    return test_state_dict, event


class SimpleStationWatcher(threading.Thread):
    """
    Simplified watcher that detects phase changes and sends test state updates.
    """

    def __init__(self, send_update_callback):
        super().__init__(daemon=True)
        self.send_update = send_update_callback
        self.last_phase = None
        self.stop_event = threading.Event()

    def run(self):
        while not self.stop_event.is_set():
            _, test_state = _get_executing_test()
            if test_state is not None:
                current_phase = (
                    test_state.running_phase_state.name
                    if test_state.running_phase_state
                    else None
                )
                if current_phase != self.last_phase:
                    test_state_dict, _ = _to_dict_with_event(test_state)
                    self.send_update(test_state_dict)
                    self.last_phase = current_phase
            sleep(0.1)  # Wait for 100 milliseconds

    def stop(self):
        self.stop_event.set()


class TofuPilot:
    """
    Context manager to automatically add an output callback to the running OpenHTF test.


    ### Usage Example:

    ```python
    from openhtf import Test
    from tofupilot import TofuPilot

    #...

    def main():
        test = Test(*your_phases, procedure_id="FVT1")

        # Stream real-time test execution data to TofuPilot
        with TofuPilot(test):
            test.execute(lambda: "SN15")
    ```
    """

    def __init__(self, test: Test, base_url: Optional[str] = None):
        self.test = test
        self.base_url = base_url
        self.loop = None
        self.update_queue = None
        self.event_loop_thread = None
        self.watcher = None
        self.shutdown_event = threading.Event()
        self.update_task = None
        self.uri = "ws://localhost:1234"
        self.room = os.environ.get("TOFUPILOT_API_KEY")

    def __enter__(self):
        # Initialize a thread-safe asyncio.Queue
        self.test.add_output_callbacks(upload(base_url=self.base_url))
        self.update_queue = asyncio.Queue()

        # Start the event loop in a separate thread
        self.event_loop_thread = threading.Thread(
            target=self.run_event_loop, daemon=True
        )
        self.event_loop_thread.start()

        # Wait until the event loop is ready
        while self.loop is None:
            sleep(0.1)

        # Start the SimpleStationWatcher with a callback to send updates
        self.watcher = SimpleStationWatcher(self.send_update)
        self.watcher.start()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Stop the StationWatcher
        if self.watcher:
            self.watcher.stop()
            self.watcher.join()

        # Schedule the shutdown coroutine
        if self.loop and not self.loop.is_closed():
            asyncio.run_coroutine_threadsafe(self.shutdown(), self.loop)

        # Wait for the event loop thread to finish
        if self.event_loop_thread:
            self.event_loop_thread.join()

    def send_update(self, message):
        """Thread-safe method to send a message to the event loop."""
        if self.loop and not self.loop.is_closed():
            asyncio.run_coroutine_threadsafe(self.update_queue.put(message), self.loop)

    def run_event_loop(self):
        """Runs the asyncio event loop in a separate thread."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.setup())
        self.loop.run_forever()

    async def setup(self):
        """Starts the update processor."""
        # Start the coroutine that processes updates
        self.update_task = asyncio.create_task(self.process_updates())

    async def process_updates(self):
        """Sends current state of the test to the websocket server"""
        ydoc = YDoc()
        async with (
            connect(f"{self.uri}/{self.room}") as websocket,
            WebsocketProvider(ydoc, websocket),
        ):
            ymap = ydoc.get_map("test_state_map")
            try:
                while True:
                    state_update = await self.update_queue.get()
                    with ydoc.begin_transaction() as txn:
                        ymap.set(txn, "test_state", state_update)
                    print("Updated test state")
            except asyncio.CancelledError:
                pass  # Handle task cancellation gracefully
        ydoc.close()

    async def shutdown(self):
        """Cleans up resources and stops the event loop."""
        # Cancel the update task
        if self.update_task is not None:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass

        # Stop the event loop
        self.loop.stop()
