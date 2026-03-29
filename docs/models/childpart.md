# ChildPart


## Fields

| Field                                                        | Type                                                         | Required                                                     | Description                                                  | Example                                                      |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| `id`                                                         | *str*                                                        | :heavy_check_mark:                                           | Part ID.                                                     | 550e8400-e29b-41d4-a716-446655440006                         |
| `number`                                                     | *str*                                                        | :heavy_check_mark:                                           | Part number.                                                 | PCB-SUB-V1                                                   |
| `name`                                                       | *str*                                                        | :heavy_check_mark:                                           | Part name.                                                   | Sub Assembly PCB                                             |
| `revision`                                                   | [Nullable[models.ChildRevision]](../models/childrevision.md) | :heavy_check_mark:                                           | Part revision information.                                   |                                                              |