from openhtf import Test

from .upload import upload


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

    def __init__(self, test: Test, base_url=None):
        self.test = test
        self.base_url = base_url

    def __enter__(self):
        self.test.add_output_callbacks(upload(base_url=self.base_url))
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass
