# ErrorFORBIDDEN

Forbidden error


## Fields

| Field                                                                | Type                                                                 | Required                                                             | Description                                                          | Example                                                              |
| -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `message`                                                            | *str*                                                                | :heavy_check_mark:                                                   | The error message                                                    | Forbidden                                                            |
| `code`                                                               | *str*                                                                | :heavy_check_mark:                                                   | The error code                                                       | FORBIDDEN                                                            |
| `issues`                                                             | List[[models.ErrorFORBIDDENIssue](../models/errorforbiddenissue.md)] | :heavy_minus_sign:                                                   | An array of issues that were responsible for the error               | []                                                                   |