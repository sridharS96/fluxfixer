
WITH dim_product_category__source  (
  SELECT
    *
  FROM `vit-lam-data.wide_world_importers.external__categories`
), dim_product_category__rename_rect  (
  SELECT
    CT(category_id  INT)  category_key,
    CT(category_name  STRING)  category_name,
    CT(parent_category_id  INT)  parent_category_key,
    CT(category_level  INT)  category_level
  FROM dim_product_category__source
), dim_product_category__handle_null  (
  SELECT
    category_key,
    IFNULL(category_name, 'Undefined')  category_name
    ,IFNULL(parent_category_key, 0)  parent_category_key
    ,IFNULL(category_level, 0)  category_level
  FROM dim_product_category__rename_rect
), dim_product_category__add_undefined  (
  SELECT
    category_key,
    category_name,
    parent_category_key,
    category_level
  FROM dim_product_category__handle_null
  UNION ALL
  SELECT
    0  category_key,
    'Undefined'  category_name,
    0  parent_category_key,
    0  category_level
  UNION ALL
  SELECT
    -1  category_key,
    'Invalid'  category_name,
    -1  parent_category_key,
    -1  category_level
), dim_category_add_parent_name  (
SELECT
  category.category_key,
  category.category_name,
  category.parent_category_key,
  parent.category_name  parent_category_name,
  category.category_level
FROM dim_product_category__add_undefined  category
LEFT JOIN dim_product_category__add_undefined  parent
  ON category.parent_category_key = parent.category_key
), category_levels  (
SELECT
  *
  , category_key  category_level_1_key
  , category_name  category_level_1_name
  , 0  category_level_2_key
  , 'Undefined'  category_level_2_name
  , 0  category_level_3_key
  , 'Undefined'  category_level_3_name
  , 0  category_level_4_key
  , 'Undefined'  category_level_4_name
FROM dim_category_add_parent_name
WHERE category_level = 1

UNION ALL
SELECT
  *
  , parent_category_key  category_level_1_key
  , parent_category_name  category_level_1_name
  , category_key  category_level_2_key
  , category_name  category_level_2_name
  , 0  category_level_3_key
  , 'Undefined'  category_level_3_name
  , 0  category_level_4_key
  , 'Undefined'  category_level_4_name
FROM dim_category_add_parent_name
WHERE category_level = 2

UNION ALL
SELECT
  l3.*
  , l12.parent_category_key  category_level_1_key
  , l12.parent_category_name  category_level_1_name
  , l3.parent_category_key  category_level_2_key
  , l3.parent_category_name  category_level_2_name
  , l3.category_key  category_level_3_key
  , l3.category_name  category_level_3_name
  , 0  category_level_4_key
  , 'Undefined'  category_level_4_name
FROM dim_category_add_parent_name  l3
LEFT JOIN dim_category_add_parent_name  l12
  ON l3.parent_category_key = l12.category_key
WHERE l3.category_level = 3

UNION ALL
SELECT
  l4.*
  , l12.parent_category_key  category_level_1_key
  , l12.parent_category_name  category_level_1_name
  , l3.parent_category_key  category_level_2_key
  , l3.parent_category_name  category_level_2_name
  , l4.parent_category_key  category_level_3_key
  , l4.parent_category_name  category_level_3_name
  , l4.category_key  category_level_4_key
  , l4.category_name  category_level_4_name
FROM dim_category_add_parent_name  l4
LEFT JOIN dim_category_add_parent_name  l3
  ON l4.parent_category_key = l3.category_key
LEFT JOIN dim_category_add_parent_name  l12
  ON l3.parent_category_key = l12.category_key
WHERE l4.category_level = 4
)

SELECT
  category_level_1_name  category_name,
  SUM(gross_amount)
FROM `atomic-oven-374400.wide_world_importers_dwh.fact_sales_order_line`  fact_sales
LEFT JOIN `atomic-oven-374400.wide_world_importers_dwh.dim_product`  dim_product
  ON fact_sales.product_key = dim_product.product_key
LEFT JOIN category_levels  dim_category
  ON dim_product.category_key = dim_category.category_key
GROUP BY category_name

UNION ALL
SELECT
  category_level_2_name  category_name,
  SUM(gross_amount)
FROM `atomic-oven-374400.wide_world_importers_dwh.fact_sales_order_line`  fact_sales
LEFT JOIN `atomic-oven-374400.wide_world_importers_dwh.dim_product`  dim_product
  ON fact_sales.product_key = dim_product.product_key
LEFT JOIN category_levels  dim_category
  ON dim_product.category_key = dim_category.category_key
WHERE category_level_2_name <> 'Undefined'
GROUP BY category_name

UNION ALL
SELECT
  category_level_3_name  category_name,
  SUM(gross_amount)
FROM `atomic-oven-374400.wide_world_importers_dwh.fact_sales_order_line`  fact_sales
LEFT JOIN `atomic-oven-374400.wide_world_importers_dwh.dim_product`  dim_product
  ON fact_sales.product_key = dim_product.product_key
LEFT JOIN category_levels  dim_category
  ON dim_product.category_key = dim_category.category_key
WHERE category_level_3_name <> 'Undefined'
GROUP BY category_name

UNION ALL
SELECT
  category_level_4_name  category_name,
  SUM(gross_amount)
FROM `atomic-oven-374400.wide_world_importers_dwh.fact_sales_order_line`  fact_sales
LEFT JOIN `atomic-oven-374400.wide_world_importers_dwh.dim_product`  dim_product
  ON fact_sales.product_key = dim_product.product_key
LEFT JOIN category_levels  dim_category
  ON dim_product.category_key = dim_category.category_key
WHERE category_level_4_name <> 'Undefined'
GROUP BY category_name;
