# ErrorUNAUTHORIZED

Unauthorized error


## Fields

| Field                                                                      | Type                                                                       | Required                                                                   | Description                                                                | Example                                                                    |
| -------------------------------------------------------------------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `message`                                                                  | *str*                                                                      | :heavy_check_mark:                                                         | The error message                                                          | Unauthorized                                                               |
| `code`                                                                     | *str*                                                                      | :heavy_check_mark:                                                         | The error code                                                             | UNAUTHORIZED                                                               |
| `issues`                                                                   | List[[models.ErrorUNAUTHORIZEDIssue](../models/errorunauthorizedissue.md)] | :heavy_minus_sign:                                                         | An array of issues that were responsible for the error                     | []                                                                         |