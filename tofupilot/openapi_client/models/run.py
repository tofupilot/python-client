import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.run_outcome import RunOutcome
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.run_logs_item import RunLogsItem
    from ..models.run_phases_item import RunPhasesItem
    from ..models.run_steps_item import RunStepsItem
    from ..models.run_sub_units_item import RunSubUnitsItem
    from ..models.run_unit_under_test import RunUnitUnderTest


T = TypeVar("T", bound="Run")


@_attrs_define
class Run:
    run_passed: bool
    procedure_id: str
    unit_under_test: Union[Unset, "RunUnitUnderTest"] = UNSET
    serial_number: Union[Unset, str] = UNSET
    part_number: Union[Unset, str] = UNSET
    batch_number: Union[Unset, str] = UNSET
    revision: Union[Unset, str] = UNSET
    sub_units: Union[Unset, list["RunSubUnitsItem"]] = UNSET
    outcome: Union[Unset, RunOutcome] = UNSET
    procedure_version: Union[None, Unset, str] = UNSET
    started_at: Union[None, Unset, datetime.datetime] = UNSET
    duration: Union[Unset, str] = "PT0S"
    ended_at: Union[Unset, datetime.datetime] = UNSET
    docstring: Union[Unset, str] = UNSET
    logs: Union[Unset, list["RunLogsItem"]] = UNSET
    phases: Union[Unset, list["RunPhasesItem"]] = UNSET
    steps: Union[Unset, list["RunStepsItem"]] = UNSET
    """ The `steps` field is deprecated in favor of `phases` and `measurements`, which provide more detailed test
    logging. Existing `steps` will be auto-converted into a `phase`, with a `measurement` if they include a numeric
    value. """
    procedure_name: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        run_passed = self.run_passed

        procedure_id = self.procedure_id

        unit_under_test: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.unit_under_test, Unset):
            unit_under_test = self.unit_under_test.to_dict()

        serial_number = self.serial_number

        part_number = self.part_number

        batch_number = self.batch_number

        revision = self.revision

        sub_units: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.sub_units, Unset):
            sub_units = []
            for sub_units_item_data in self.sub_units:
                sub_units_item = sub_units_item_data.to_dict()
                sub_units.append(sub_units_item)

        outcome: Union[Unset, str] = UNSET
        if not isinstance(self.outcome, Unset):
            outcome = self.outcome.value

        procedure_version: Union[None, Unset, str]
        if isinstance(self.procedure_version, Unset):
            procedure_version = UNSET
        else:
            procedure_version = self.procedure_version

        started_at: Union[None, Unset, str]
        if isinstance(self.started_at, Unset):
            started_at = UNSET
        elif isinstance(self.started_at, datetime.datetime):
            started_at = self.started_at.isoformat()
        else:
            started_at = self.started_at

        duration = self.duration

        ended_at: Union[Unset, str] = UNSET
        if not isinstance(self.ended_at, Unset):
            ended_at = self.ended_at.isoformat()

        docstring = self.docstring

        logs: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.logs, Unset):
            logs = []
            for logs_item_data in self.logs:
                logs_item = logs_item_data.to_dict()
                logs.append(logs_item)

        phases: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.phases, Unset):
            phases = []
            for phases_item_data in self.phases:
                phases_item = phases_item_data.to_dict()
                phases.append(phases_item)

        steps: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.steps, Unset):
            steps = []
            for steps_item_data in self.steps:
                steps_item = steps_item_data.to_dict()
                steps.append(steps_item)

        procedure_name: Union[None, Unset, str]
        if isinstance(self.procedure_name, Unset):
            procedure_name = UNSET
        else:
            procedure_name = self.procedure_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "run_passed": run_passed,
                "procedure_id": procedure_id,
            }
        )
        if unit_under_test is not UNSET:
            field_dict["unit_under_test"] = unit_under_test
        if serial_number is not UNSET:
            field_dict["serial_number"] = serial_number
        if part_number is not UNSET:
            field_dict["part_number"] = part_number
        if batch_number is not UNSET:
            field_dict["batch_number"] = batch_number
        if revision is not UNSET:
            field_dict["revision"] = revision
        if sub_units is not UNSET:
            field_dict["sub_units"] = sub_units
        if outcome is not UNSET:
            field_dict["outcome"] = outcome
        if procedure_version is not UNSET:
            field_dict["procedure_version"] = procedure_version
        if started_at is not UNSET:
            field_dict["started_at"] = started_at
        if duration is not UNSET:
            field_dict["duration"] = duration
        if ended_at is not UNSET:
            field_dict["ended_at"] = ended_at
        if docstring is not UNSET:
            field_dict["docstring"] = docstring
        if logs is not UNSET:
            field_dict["logs"] = logs
        if phases is not UNSET:
            field_dict["phases"] = phases
        if steps is not UNSET:
            field_dict["steps"] = steps
        if procedure_name is not UNSET:
            field_dict["procedure_name"] = procedure_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_logs_item import RunLogsItem
        from ..models.run_phases_item import RunPhasesItem
        from ..models.run_steps_item import RunStepsItem
        from ..models.run_sub_units_item import RunSubUnitsItem
        from ..models.run_unit_under_test import RunUnitUnderTest

        d = dict(src_dict)
        run_passed = d.pop("run_passed")

        procedure_id = d.pop("procedure_id")

        _unit_under_test = d.pop("unit_under_test", UNSET)
        unit_under_test: Union[Unset, RunUnitUnderTest]
        if isinstance(_unit_under_test, Unset):
            unit_under_test = UNSET
        else:
            unit_under_test = RunUnitUnderTest.from_dict(_unit_under_test)

        serial_number = d.pop("serial_number", UNSET)

        part_number = d.pop("part_number", UNSET)

        batch_number = d.pop("batch_number", UNSET)

        revision = d.pop("revision", UNSET)

        sub_units = []
        _sub_units = d.pop("sub_units", UNSET)
        for sub_units_item_data in _sub_units or []:
            sub_units_item = RunSubUnitsItem.from_dict(sub_units_item_data)

            sub_units.append(sub_units_item)

        _outcome = d.pop("outcome", UNSET)
        outcome: Union[Unset, RunOutcome]
        if isinstance(_outcome, Unset):
            outcome = UNSET
        else:
            outcome = RunOutcome(_outcome)

        def _parse_procedure_version(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        procedure_version = _parse_procedure_version(d.pop("procedure_version", UNSET))

        def _parse_started_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                started_at_type_0 = isoparse(data)

                return started_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        started_at = _parse_started_at(d.pop("started_at", UNSET))

        duration = d.pop("duration", UNSET)

        _ended_at = d.pop("ended_at", UNSET)
        ended_at: Union[Unset, datetime.datetime]
        if isinstance(_ended_at, Unset):
            ended_at = UNSET
        else:
            ended_at = isoparse(_ended_at)

        docstring = d.pop("docstring", UNSET)

        logs = []
        _logs = d.pop("logs", UNSET)
        for logs_item_data in _logs or []:
            logs_item = RunLogsItem.from_dict(logs_item_data)

            logs.append(logs_item)

        phases = []
        _phases = d.pop("phases", UNSET)
        for phases_item_data in _phases or []:
            phases_item = RunPhasesItem.from_dict(phases_item_data)

            phases.append(phases_item)

        steps = []
        _steps = d.pop("steps", UNSET)
        for steps_item_data in _steps or []:
            steps_item = RunStepsItem.from_dict(steps_item_data)

            steps.append(steps_item)

        def _parse_procedure_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        procedure_name = _parse_procedure_name(d.pop("procedure_name", UNSET))

        run = cls(
            run_passed=run_passed,
            procedure_id=procedure_id,
            unit_under_test=unit_under_test,
            serial_number=serial_number,
            part_number=part_number,
            batch_number=batch_number,
            revision=revision,
            sub_units=sub_units,
            outcome=outcome,
            procedure_version=procedure_version,
            started_at=started_at,
            duration=duration,
            ended_at=ended_at,
            docstring=docstring,
            logs=logs,
            phases=phases,
            steps=steps,
            procedure_name=procedure_name,
        )

        run.additional_properties = d
        return run

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
