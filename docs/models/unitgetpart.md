# UnitGetPart

Part information with revision details for this unit. Every unit must have a part and revision.


## Fields

| Field                                                               | Type                                                                | Required                                                            | Description                                                         | Example                                                             |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `id`                                                                | *str*                                                               | :heavy_check_mark:                                                  | Part ID.                                                            | 550e8400-e29b-41d4-a716-446655440007                                |
| `number`                                                            | *str*                                                               | :heavy_check_mark:                                                  | Part number.                                                        | PCB-MAIN-001                                                        |
| `name`                                                              | *str*                                                               | :heavy_check_mark:                                                  | Part name.                                                          | Main Control Board                                                  |
| `revision`                                                          | [models.UnitGetRevision](../models/unitgetrevision.md)              | :heavy_check_mark:                                                  | Revision information for this unit.                                 | {<br/>"id": "550e8400-e29b-41d4-a716-446655440006",<br/>"number": "REV-A"<br/>} |