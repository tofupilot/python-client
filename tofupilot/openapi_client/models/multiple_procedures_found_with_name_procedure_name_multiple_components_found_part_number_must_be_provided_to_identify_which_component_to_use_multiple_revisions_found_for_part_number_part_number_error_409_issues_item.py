from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar(
    "T",
    bound="MultipleProceduresFoundWithNameProcedureNameMultipleComponentsFoundPartNumberMustBeProvidedToIdentifyWhichComponentToUseMultipleRevisionsFoundForPartNumberPartNumberError409IssuesItem",
)


@_attrs_define
class MultipleProceduresFoundWithNameProcedureNameMultipleComponentsFoundPartNumberMustBeProvidedToIdentifyWhichComponentToUseMultipleRevisionsFoundForPartNumberPartNumberError409IssuesItem:
    message: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        message = self.message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "message": message,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        message = d.pop("message")

        multiple_procedures_found_with_name_procedure_name_multiple_components_found_part_number_must_be_provided_to_identify_which_component_to_use_multiple_revisions_found_for_part_number_part_number_error_409_issues_item = cls(
            message=message,
        )

        multiple_procedures_found_with_name_procedure_name_multiple_components_found_part_number_must_be_provided_to_identify_which_component_to_use_multiple_revisions_found_for_part_number_part_number_error_409_issues_item.additional_properties = d
        return multiple_procedures_found_with_name_procedure_name_multiple_components_found_part_number_must_be_provided_to_identify_which_component_to_use_multiple_revisions_found_for_part_number_part_number_error_409_issues_item

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
