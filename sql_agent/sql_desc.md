# MySQL数据库数据字典

本数据字典记录了MySQL数据库中各张数据表的基本情况。

## 1.pollutant_hourly_data数据表

- 基本解释

    pollutant_hourly_data数据表记录了各地区6中常见污染物的小时数据，主要字段包括：时间（time）、地点(location)、地点类型(location_type)、上级地点(upper_location)、污染物名称(pollutant_name)、污染数值(pollutant_value)。
  
- 数据来源
  ​		pollutant_hourly_data数据表由数据监测设备自动采集记录，数据集的准确性和可信度都非常高。

- 各字段说明

| Column Name | Description | Value Range | Value Explanation | Type |
|-------------|-------------|-------------|-------------------|------|
| time | 时间 |   | 数据基本格式为：2022-01-01 00:00:00 | DATETIME |
| location | 地点名称 |  | 比如：北京，丰台区，丰台小屯站等 | VARCHAR(255) |
| location_type | 地点类型 | 1, 2, 3, 4, 5 | 1表示省级，2表示市级，3表示区级，4表示街道级，5表示站点级 | INT |
| upper_location | 上级地点 |  | 比如：北京，丰台区，丰台小屯站等 | VARCHAR(255) |
| pollutant_name | 污染物名称 | PM2.5, PM10, SO2, NO2, CO, O3 | 只包含6种常见的大气污染数据 | VARCHAR(255) |
| pollutant_value | 污染数值 |  | 单位为ug/m3 | FLOAT |