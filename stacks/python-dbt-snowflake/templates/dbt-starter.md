# dbt Project Starter Template

## Project Scaffold

```
{project-name}/
  dbt_project.yml         (project name, profile, model configs by directory)
  profiles.yml            (connection — dev schema = personal, prod schema = analytics)
  packages.yml            (dbt-utils, dbt-expectations, dbt-checkpoint)
  .sqlfluff               (dialect: snowflake, rules config)
  models/
    staging/
      _sources.yml        ({{ source() }} definitions for all raw tables)
      stg_{source}_{table}.sql
      _stg_{source}_{table}.yml
    intermediate/         (optional)
      int_{name}.sql
      _int_{name}.yml
    marts/
      fct_{name}.sql
      _fct_{name}.yml
      dim_{name}.sql
      _dim_{name}.yml
  tests/
    assert_{condition}.sql
  macros/
    {utility_name}.sql
  seeds/
    {lookup_table}.csv    (small static reference data)
```

---

## Example `dbt_project.yml`

```yaml
name: '{project_name}'
version: '1.0.0'
config-version: 2

profile: '{project_name}'

model-paths: ["models"]
test-paths: ["tests"]
macro-paths: ["macros"]
seed-paths: ["seeds"]

models:
  {project_name}:
    staging:
      +materialized: view
      +schema: staging
    intermediate:
      +materialized: ephemeral
    marts:
      +materialized: table
      +schema: marts
      facts:
        +materialized: incremental
```

---

## Example `profiles.yml`

```yaml
{project_name}:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: "{{ env_var('SNOWFLAKE_ACCOUNT') }}"
      user: "{{ env_var('SNOWFLAKE_USER') }}"
      private_key_path: "{{ env_var('SNOWFLAKE_PRIVATE_KEY_PATH') }}"
      private_key_passphrase: "{{ env_var('SNOWFLAKE_PRIVATE_KEY_PASSPHRASE', '') }}"
      role: transformer_dev
      database: analytics_dev
      warehouse: transforming_xs
      schema: "dbt_{{ env_var('DBT_USER', 'dev') }}"
      threads: 4
    prod:
      type: snowflake
      account: "{{ env_var('SNOWFLAKE_ACCOUNT') }}"
      user: "{{ env_var('SNOWFLAKE_USER') }}"
      private_key_path: "{{ env_var('SNOWFLAKE_PRIVATE_KEY_PATH') }}"
      private_key_passphrase: "{{ env_var('SNOWFLAKE_PRIVATE_KEY_PASSPHRASE', '') }}"
      role: transformer_prod
      database: analytics
      warehouse: transforming_m
      schema: analytics
      threads: 8
```

> **Auth note**: Snowflake deprecated password auth for service accounts. Use key-pair auth above. 
> Generate key: `openssl genrsa -out ~/.ssh/snowflake_key.p8 2048`
> Set SNOWFLAKE_PRIVATE_KEY_PATH to the path of the key file.

---

## Example `packages.yml`

```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: [">=1.1.0", "<2.0.0"]
  - package: calogica/dbt_expectations
    version: [">=0.10.0", "<1.0.0"]
  - package: dbt-labs/dbt_project_evaluator
    version: [">=0.8.0", "<1.0.0"]
```

Run `dbt deps` after updating packages.

---

## Example `_sources.yml`

```yaml
version: 2

sources:
  - name: raw_ecommerce
    database: raw
    schema: ecommerce
    freshness:
      warn_after: {count: 24, period: hour}
      error_after: {count: 48, period: hour}
    loaded_at_field: _loaded_at
    tables:
      - name: orders
        description: "Raw orders from the transactional database."
      - name: order_items
        description: "Raw line items for each order."
      - name: customers
        description: "Raw customer records."
```

---

## Example Staging Model `.yml`

```yaml
version: 2

models:
  - name: stg_orders
    description: "Staged orders, 1:1 with raw.ecommerce.orders. Renamed and typed."
    columns:
      - name: order_id
        description: "Unique order identifier."
        data_tests:
          - not_null
          - unique
      - name: customer_id
        description: "Foreign key to stg_customers."
        data_tests:
          - not_null
          - relationships:
              to: ref('stg_customers')
              field: customer_id
      - name: order_date
        description: "Date the order was placed, cast from created_at timestamp."
        data_tests:
          - not_null
      - name: status
        description: "Current order status."
        data_tests:
          - not_null
          - accepted_values:
              values: ['placed', 'shipped', 'completed', 'cancelled']
```

---

## Example `.sqlfluff`

```ini
[sqlfluff]
dialect = snowflake
templater = dbt
max_line_length = 120
exclude_rules = AM04

[sqlfluff:templater:dbt]
project_dir = .

[sqlfluff:rules:layout.indent]
indent_unit = space
tab_space_size = 4

[sqlfluff:rules:capitalisation.keywords]
capitalisation_policy = upper

[sqlfluff:rules:capitalisation.functions]
extended_capitalisation_policy = upper

[sqlfluff:rules:aliasing.table]
aliasing = explicit

[sqlfluff:rules:aliasing.column]
aliasing = explicit
```

---

## Quickstart Commands

```bash
# Install dependencies
dbt deps

# Validate connections and compile
dbt debug
dbt compile

# Run staging models only
dbt run --select staging

# Run + test a single model
dbt build --select stg_orders

# Run full project
dbt build

# Incremental CI (changed models + downstream)
dbt build --select state:modified+

# Generate and serve docs
dbt docs generate
dbt docs serve

# Check source freshness
dbt source freshness

# Lint SQL
sqlfluff lint --dialect snowflake models/
```
