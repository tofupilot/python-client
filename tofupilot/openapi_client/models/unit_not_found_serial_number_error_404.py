from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.unit_not_found_serial_number_error_404_issues_item import UnitNotFoundSerialNumberError404IssuesItem


T = TypeVar("T", bound="UnitNotFoundSerialNumberError404")


@_attrs_define
class UnitNotFoundSerialNumberError404:
    """The error information

    Example:
        {'code': 'NOT_FOUND', 'message': 'Unit not found: {serialNumber}', 'issues': []}

    """

    message: str
    """ The error message """
    code: str
    """ The error code """
    issues: Union[Unset, list["UnitNotFoundSerialNumberError404IssuesItem"]] = UNSET
    """ An array of issues that were responsible for the error """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        message = self.message

        code = self.code

        issues: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.issues, Unset):
            issues = []
            for issues_item_data in self.issues:
                issues_item = issues_item_data.to_dict()
                issues.append(issues_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "message": message,
                "code": code,
            }
        )
        if issues is not UNSET:
            field_dict["issues"] = issues

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.unit_not_found_serial_number_error_404_issues_item import (
            UnitNotFoundSerialNumberError404IssuesItem,
        )

        d = dict(src_dict)
        message = d.pop("message")

        code = d.pop("code")

        issues = []
        _issues = d.pop("issues", UNSET)
        for issues_item_data in _issues or []:
            issues_item = UnitNotFoundSerialNumberError404IssuesItem.from_dict(issues_item_data)

            issues.append(issues_item)

        unit_not_found_serial_number_error_404 = cls(
            message=message,
            code=code,
            issues=issues,
        )

        unit_not_found_serial_number_error_404.additional_properties = d
        return unit_not_found_serial_number_error_404

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
