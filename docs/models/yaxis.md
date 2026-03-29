# YAxis

Data series with numeric data, unit, and optional validators/aggregations.


## Fields

| Field                                                            | Type                                                             | Required                                                         | Description                                                      | Example                                                          |
| ---------------------------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------- |
| `data`                                                           | List[*float*]                                                    | :heavy_check_mark:                                               | Array of numeric data points for this axis.                      | [<br/>0,<br/>1,<br/>2,<br/>3,<br/>4<br/>]                        |
| `units`                                                          | *OptionalNullable[str]*                                          | :heavy_minus_sign:                                               | Unit for this axis.                                              | V                                                                |
| `description`                                                    | *OptionalNullable[str]*                                          | :heavy_minus_sign:                                               | Description of this data series.                                 | Output voltage                                                   |
| `validators`                                                     | List[[models.YAxisValidators](../models/yaxisvalidators.md)]     | :heavy_minus_sign:                                               | Validators for this specific axis/series.                        |                                                                  |
| `aggregations`                                                   | List[[models.YAxisAggregations](../models/yaxisaggregations.md)] | :heavy_minus_sign:                                               | Aggregations computed over this axis data (min, max, avg, etc.). |                                                                  |