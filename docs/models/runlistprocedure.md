# RunListProcedure

Test procedure associated with this run.


## Fields

| Field                                                             | Type                                                              | Required                                                          | Description                                                       | Example                                                           |
| ----------------------------------------------------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------------- |
| `id`                                                              | *str*                                                             | :heavy_check_mark:                                                | Procedure ID.                                                     | 550e8400-e29b-41d4-a716-446655440003                              |
| `name`                                                            | *str*                                                             | :heavy_check_mark:                                                | Procedure name.                                                   | PCB Functional Test                                               |
| `version`                                                         | [Nullable[models.RunListVersion]](../models/runlistversion.md)    | :heavy_check_mark:                                                | Version of the procedure used for this run.                       | {<br/>"id": "550e8400-e29b-41d4-a716-446655440010",<br/>"tag": "v2.1.0"<br/>} |