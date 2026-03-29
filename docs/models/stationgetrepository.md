# StationGetRepository


## Fields

| Field                                                        | Type                                                         | Required                                                     | Description                                                  | Example                                                      |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| `owner`                                                      | *str*                                                        | :heavy_check_mark:                                           | Repository owner                                             | tofupilot                                                    |
| `name`                                                       | *str*                                                        | :heavy_check_mark:                                           | Repository name                                              | procedures                                                   |
| `provider`                                                   | [models.StationGetProvider](../models/stationgetprovider.md) | :heavy_check_mark:                                           | Git provider                                                 | github                                                       |
| `gitlab_project_id`                                          | *Nullable[float]*                                            | :heavy_check_mark:                                           | GitLab project ID (only for GitLab repos)                    | 12345                                                        |