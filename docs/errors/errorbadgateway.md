# ErrorBADGATEWAY

Bad gateway error


## Fields

| Field                                                                  | Type                                                                   | Required                                                               | Description                                                            | Example                                                                |
| ---------------------------------------------------------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `message`                                                              | *str*                                                                  | :heavy_check_mark:                                                     | The error message                                                      | Bad gateway                                                            |
| `code`                                                                 | *str*                                                                  | :heavy_check_mark:                                                     | The error code                                                         | BAD_GATEWAY                                                            |
| `issues`                                                               | List[[models.ErrorBADGATEWAYIssue](../models/errorbadgatewayissue.md)] | :heavy_minus_sign:                                                     | An array of issues that were responsible for the error                 | []                                                                     |