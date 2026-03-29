# UserListResponse


## Fields

| Field                                | Type                                 | Required                             | Description                          | Example                              |
| ------------------------------------ | ------------------------------------ | ------------------------------------ | ------------------------------------ | ------------------------------------ |
| `id`                                 | *str*                                | :heavy_check_mark:                   | Unique identifier for the user.      | 550e8400-e29b-41d4-a716-446655440000 |
| `email`                              | *str*                                | :heavy_check_mark:                   | Email address of the user.           | john.doe@example.com                 |
| `name`                               | *Nullable[str]*                      | :heavy_check_mark:                   | Display name of the user.            | John Doe                             |
| `image`                              | *Nullable[str]*                      | :heavy_check_mark:                   | Profile image URL for the user.      | https://example.com/user-avatar.jpg  |
| `banned`                             | *bool*                               | :heavy_check_mark:                   | Whether the user is banned.          | false                                |