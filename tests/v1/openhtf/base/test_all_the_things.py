"""
Adapted from https://github.com/tofupilot/examples/blob/aad0dc20dd10b55a24378e9b6754712d3401d386/testing_examples/openhtf/all_the_things
And https://github.com/tofupilot/examples/tree/aad0dc20dd10b55a24378e9b6754712d3401d386/testing_examples/openhtf/without_streaming
"""

import os.path
import time

import openhtf as htf
from openhtf import util
from openhtf.output import callbacks
from openhtf.output.callbacks import console_summary, json_factory
from openhtf.util import units
from tofupilot.openhtf import TofuPilot

@htf.measures(
    htf.Measurement("widget_type")
    .matches_regex(r".*Widget$")
    .doc("""This measurement tracks the type of widgets."""),
    htf.Measurement("widget_color").doc("Color of the widget"),
    htf.Measurement("widget_size").in_range(1, 4).doc("Size of widget"),
)
@htf.measures(
    "specified_as_args",
    docstring="Helpful docstring",
    units=units.HERTZ,
    validators=[util.validators.matches_regex("Measurement")],
)
def hello_world(test):
    """A hello world test phase."""
    test.logger.info("Hello World!")
    test.measurements.widget_type = "MyWidget"
    test.measurements.widget_color = "Black"
    test.measurements.widget_size = 3
    test.measurements.specified_as_args = "Measurement args specified directly"


# Timeout if this phase takes longer than 10 seconds.
@htf.PhaseOptions(timeout_s=10)
@htf.measures(*(htf.Measurement("level_%s" % i)
              for i in ["none", "some", "all"]))
def set_measurements(test):
    """Test phase that sets a measurement."""
    test.measurements.level_none = 0
    time.sleep(1)
    test.measurements.level_some = 8
    time.sleep(1)
    test.measurements.level_all = 9
    time.sleep(1)
    level_all = test.get_measurement("level_all")
    assert level_all.value == 9


@htf.measures(
    htf.Measurement("dimensions").with_dimensions(units.HERTZ),
    htf.Measurement("lots_of_dims").with_dimensions(
        units.HERTZ,
        units.SECOND,
        htf.Dimension(description="my_angle", unit=units.RADIAN),
    ),
)
def dimensions(test):
    """Phase with dimensioned measurements."""
    for dim in range(5):
        test.measurements.dimensions[dim] = 1 << dim
    for x, y, z in zip(
        list(
            range(
            1, 5)), list(
                range(
                    21, 25)), list(
                        range(
                            101, 105))):
        test.measurements.lots_of_dims[x, y, z] = x + y + z


@htf.measures(
    htf.Measurement("replaced_min_only").in_range(
        "{minimum}", 5, type=int), htf.Measurement("replaced_max_only").in_range(
            0, "{maximum}", type=int), htf.Measurement("replaced_min_max").in_range(
                "{minimum}", "{maximum}", type=int), )
def measures_with_args(test, minimum, maximum):
    """Phase with measurement with arguments."""
    del minimum  # Unused.
    del maximum  # Unused.
    test.measurements.replaced_min_only = 1
    test.measurements.replaced_max_only = 1
    test.measurements.replaced_min_max = 1


@htf.measures(
    htf.Measurement("replaced_marginal_min_only").in_range(
        0, 10, "{marginal_minimum}", 8, type=int
    ),
    htf.Measurement("replaced_marginal_max_only").in_range(
        0, 10, 2, "{marginal_maximum}", type=int
    ),
    htf.Measurement("replaced_marginal_min_max").in_range(
        0, 10, "{marginal_minimum}", "{marginal_maximum}", type=int
    ),
)
def measures_with_marginal_args(test, marginal_minimum, marginal_maximum):
    """Phase with measurement with marginal arguments."""
    del marginal_minimum  # Unused.
    del marginal_maximum  # Unused.
    test.measurements.replaced_marginal_min_only = 3
    test.measurements.replaced_marginal_max_only = 3
    test.measurements.replaced_marginal_min_max = 3


def attachments(test):
    test.attach(
        "test_attachment",
        "This is test attachment data.".encode("utf-8"))
    test.attach_from_file("tests/v1/attachments/oscilloscope.jpeg")

    test_attachment = test.get_attachment("test_attachment")
    assert test_attachment.data == b"This is test attachment data."


@htf.PhaseOptions(run_if=lambda: False)
def skip_phase():
    """Don't run this phase."""


def analysis(test):  # pylint: disable=missing-function-docstring
    level_all = test.get_measurement("level_all")
    assert level_all.value == 9
    test_attachment = test.get_attachment("test_attachment")
    assert test_attachment.data == b"This is test attachment data."
    lots_of_dims = test.get_measurement("lots_of_dims")
    assert lots_of_dims.value.value == [
        (1, 21, 101, 123),
        (2, 22, 102, 126),
        (3, 23, 103, 129),
        (4, 24, 104, 132),
    ]

def teardown(test):
    test.logger.info("Running teardown")

def test_all_the_things(tofupilot_server_url, api_key, stream_enabled, procedure_identifier, procedure_id, tmp_path, extract_id_and_check_run_exists):
    test = htf.Test(
        htf.PhaseGroup.with_teardown(teardown)(
            hello_world,
            set_measurements,
            dimensions,
            attachments,
            skip_phase,
            measures_with_args.with_args(minimum=1, maximum=4),
            measures_with_marginal_args.with_args(
                marginal_minimum=4, marginal_maximum=6
            ),
            analysis,
        ),
        test_name="MyTest",
        test_description="OpenHTF Example Test",
        test_version="1.0.0",
        part_number="PCB01",
        procedure_id=procedure_identifier,
    )

    # TODO: Re-enable once https://github.com/google/openhtf/issues/1242 is fixed
    """test.add_output_callbacks(
        callbacks.OutputToFile(
            str(tmp_path) + "/{dut_id}.{metadata[test_name]}.{start_time_millis}.pickle"
        )
    )"""

    
    test.add_output_callbacks(
        json_factory.OutputToJSON(
            str(tmp_path) + "/{dut_id}.{metadata[test_name]}.{start_time_millis}.json",
            indent=4
        )
    )

    test.add_output_callbacks(console_summary.ConsoleSummary())
    
    with TofuPilot(test, url=tofupilot_server_url, api_key=api_key, stream=stream_enabled):
        test.execute(lambda: "00220D4K")


    extract_id_and_check_run_exists(serial_number="00220D4K", part_number="PCB01", procedure_id=procedure_id)
    

