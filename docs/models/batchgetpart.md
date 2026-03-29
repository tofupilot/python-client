# BatchGetPart

Part information with revision details for this unit.


## Fields

| Field                                                    | Type                                                     | Required                                                 | Description                                              | Example                                                  |
| -------------------------------------------------------- | -------------------------------------------------------- | -------------------------------------------------------- | -------------------------------------------------------- | -------------------------------------------------------- |
| `id`                                                     | *str*                                                    | :heavy_check_mark:                                       | Part ID.                                                 | 550e8400-e29b-41d4-a716-446655440007                     |
| `number`                                                 | *str*                                                    | :heavy_check_mark:                                       | Part number.                                             | PCB-MAIN-001                                             |
| `name`                                                   | *str*                                                    | :heavy_check_mark:                                       | Part name.                                               | Main Control Board                                       |
| `revision`                                               | [models.BatchGetRevision](../models/batchgetrevision.md) | :heavy_check_mark:                                       | Revision information for this unit.                      |                                                          |