# StationUpdateRequestBody


## Fields

| Field                                                            | Type                                                             | Required                                                         | Description                                                      | Example                                                          |
| ---------------------------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------- |
| `name`                                                           | *Optional[str]*                                                  | :heavy_minus_sign:                                               | New name for the station                                         | Assembly Station 2                                               |
| `image_id`                                                       | *Optional[str]*                                                  | :heavy_minus_sign:                                               | Upload ID for the station image, or empty string to remove image |                                                                  |
| `team_id`                                                        | *OptionalNullable[str]*                                          | :heavy_minus_sign:                                               | Team ID to assign this station to, or null to unassign           | 550e8400-e29b-41d4-a716-446655440002                             |