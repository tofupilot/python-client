# PartUpdateResponse

Part updated successfully


## Fields

| Field                                                                | Type                                                                 | Required                                                             | Description                                                          | Example                                                              |
| -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `id`                                                                 | *str*                                                                | :heavy_check_mark:                                                   | Unique database identifier of the updated part.                      | 550e8400-e29b-41d4-a716-446655440000                                 |
| `number`                                                             | *str*                                                                | :heavy_check_mark:                                                   | Unique part number identifier.                                       | PCB-V3.0                                                             |
| `name`                                                               | *str*                                                                | :heavy_check_mark:                                                   | Human-readable name of the part.                                     | Updated PCB Board                                                    |
| `updated_at`                                                         | [date](https://docs.python.org/3/library/datetime.html#date-objects) | :heavy_check_mark:                                                   | ISO 8601 timestamp when the part was updated.                        | 2024-01-15T10:30:00.000Z                                             |