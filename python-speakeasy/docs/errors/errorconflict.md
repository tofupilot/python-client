# ErrorCONFLICT

Conflict error


## Fields

| Field                                                              | Type                                                               | Required                                                           | Description                                                        | Example                                                            |
| ------------------------------------------------------------------ | ------------------------------------------------------------------ | ------------------------------------------------------------------ | ------------------------------------------------------------------ | ------------------------------------------------------------------ |
| `message`                                                          | *str*                                                              | :heavy_check_mark:                                                 | The error message                                                  | Conflict                                                           |
| `code`                                                             | *str*                                                              | :heavy_check_mark:                                                 | The error code                                                     | CONFLICT                                                           |
| `issues`                                                           | List[[models.ErrorCONFLICTIssue](../models/errorconflictissue.md)] | :heavy_minus_sign:                                                 | An array of issues that were responsible for the error             | []                                                                 |