# BatchListMeta

Pagination metadata.


## Fields

| Field                                         | Type                                          | Required                                      | Description                                   | Example                                       |
| --------------------------------------------- | --------------------------------------------- | --------------------------------------------- | --------------------------------------------- | --------------------------------------------- |
| `has_more`                                    | *bool*                                        | :heavy_check_mark:                            | Whether there are more results available.     | true                                          |
| `next_cursor`                                 | *Nullable[int]*                               | :heavy_check_mark:                            | Cursor for fetching the next page of results. | 50                                            |