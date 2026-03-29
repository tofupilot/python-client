# ParentPart


## Fields

| Field                                                          | Type                                                           | Required                                                       | Description                                                    | Example                                                        |
| -------------------------------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------- |
| `id`                                                           | *str*                                                          | :heavy_check_mark:                                             | Part ID.                                                       | 550e8400-e29b-41d4-a716-446655440003                           |
| `number`                                                       | *str*                                                          | :heavy_check_mark:                                             | Part number.                                                   | PCB-MAIN-V2                                                    |
| `name`                                                         | *str*                                                          | :heavy_check_mark:                                             | Part name.                                                     | Main PCB Assembly                                              |
| `revision`                                                     | [Nullable[models.ParentRevision]](../models/parentrevision.md) | :heavy_check_mark:                                             | Part revision information.                                     |                                                                |