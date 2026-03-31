# StationListRequest


## Fields

| Field                                      | Type                                       | Required                                   | Description                                | Example                                    |
| ------------------------------------------ | ------------------------------------------ | ------------------------------------------ | ------------------------------------------ | ------------------------------------------ |
| `limit`                                    | *Optional[int]*                            | :heavy_minus_sign:                         | Number of stations to return per page      | 50                                         |
| `cursor`                                   | *Optional[int]*                            | :heavy_minus_sign:                         | N/A                                        | 1                                          |
| `search_query`                             | *Optional[str]*                            | :heavy_minus_sign:                         | N/A                                        | assembly                                   |
| `procedure_ids`                            | List[*str*]                                | :heavy_minus_sign:                         | N/A                                        | [<br/>"550e8400-e29b-41d4-a716-446655440000"<br/>] |