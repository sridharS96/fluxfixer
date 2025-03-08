
WITH dim_category_map_bridge__generate as                   (
       select 
        *
    FROM {{ ref('dim_category') }}
)
   select 
    category_name as                   parent_category,
    category_name as                   child_category
FROM dim_category_map_bridge__generate

union ALL
   select 
    parent_category_name as                   parent_category,
    category_name as                   child_category
FROM dim_category_map_bridge__generate
WHERE parent_category_key <> 0

union ALL
   select 
    parent.parent_category_name as                   parent_category,
    child.category_name as                   child_category
FROM dim_category_map_bridge__generate as                   child
LEFT JOIN dim_category_map_bridge__generate as                   parent
    ON child.parent_category_name = parent.category_name
WHERE parent.parent_category_key <> 0

union ALL
   select 
    parent.parent_category_name as parrent_category,
    child.category_name as child_category
FROM dim_category_map_bridge__generate as child
LEFT JOIN dim_category_map_bridge__generate as intermediate
    ON child.parent_category_name = intermediate.category_name
LEFT JOIN dim_category_map_bridge__generate parent
    ON intermediate.parent_category_name = parent.category_name
WHERE parent.parent_category_key <> 0

;
