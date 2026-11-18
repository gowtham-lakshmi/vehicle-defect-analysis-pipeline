{{ config(materialized="table") }}
with
    runs as (
        select
            release_id,
            count(*) as total_runs,
            sum(is_pass) as passed,
            sum(is_fail) as failed
        from {{ ref("fact_test_runs") }}
        group by release_id
    ),
    bugs as (
        select
            release_id,
            count(*) as total_bugs,
            sum(case when severity = 'Critical' then 1 else 0 end) as critical_bugs
        from {{ ref("fact_bugs") }}
        group by release_id
    )
select
    r.release_id,
    r.model,
    r.variant,
    r.sw_version,
    r.release_type,
    runs.total_runs,
    runs.passed,
    runs.failed,
    round(100.0 * runs.passed / runs.total_runs, 2) as pass_rate_pct,
    coalesce(bugs.total_bugs, 0) as total_bugs,
    coalesce(bugs.critical_bugs, 0) as critical_bugs
from {{ ref("dim_release") }} r
join runs on r.release_id = runs.release_id
left join bugs on r.release_id = bugs.release_id
