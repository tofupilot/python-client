# ErrorNOTFOUND

Not found error


## Fields

| Field                                                              | Type                                                               | Required                                                           | Description                                                        | Example                                                            |
| ------------------------------------------------------------------ | ------------------------------------------------------------------ | ------------------------------------------------------------------ | ------------------------------------------------------------------ | ------------------------------------------------------------------ |
| `message`                                                          | *str*                                                              | :heavy_check_mark:                                                 | The error message                                                  | Not found                                                          |
| `code`                                                             | *str*                                                              | :heavy_check_mark:                                                 | The error code                                                     | NOT_FOUND                                                          |
| `issues`                                                           | List[[models.ErrorNOTFOUNDIssue](../models/errornotfoundissue.md)] | :heavy_minus_sign:                                                 | An array of issues that were responsible for the error             | []                                                                 |