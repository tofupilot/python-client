# ErrorBADREQUEST

Bad request error


## Fields

| Field                                                                  | Type                                                                   | Required                                                               | Description                                                            | Example                                                                |
| ---------------------------------------------------------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `message`                                                              | *str*                                                                  | :heavy_check_mark:                                                     | The error message                                                      | Bad request                                                            |
| `code`                                                                 | *str*                                                                  | :heavy_check_mark:                                                     | The error code                                                         | BAD_REQUEST                                                            |
| `issues`                                                               | List[[models.ErrorBADREQUESTIssue](../models/errorbadrequestissue.md)] | :heavy_minus_sign:                                                     | An array of issues that were responsible for the error                 | []                                                                     |