
WITH dim_category_map_bridge__generate AS (
    SELECT
        *
    FROM {{ ref('dim_category') }}
)
SELECT
    category_name AS parent_category,
    category_name AS child_category
FROM dim_category_map_bridge__generate

UNION ALL
SELECT
    parent_category_name AS parent_category,
    category_name AS child_category
FROM dim_category_map_bridge__generate
WHERE parent_category_key <> 0

UNION ALL
SELECT
    parent.parent_category_name AS parent_category,
    child.category_name AS child_category
FROM dim_category_map_bridge__generate AS child
LEFT JOIN dim_category_map_bridge__generate AS parent
    ON child.parent_category_name = parent.category_name
WHERE parent.parent_category_key <> 0

UNION ALL
SELECT
    parent.parent_category_name AS parrent_category,
    child.category_name AS child_category
FROM dim_category_map_bridge__generate AS child
LEFT JOIN dim_category_map_bridge__generate AS intermediate
    ON child.parent_category_name = intermediate.category_name
LEFT JOIN dim_category_map_bridge__generate AS parent
    ON intermediate.parent_category_name = parent.category_name
WHERE parent.parent_category_key <> 0;
