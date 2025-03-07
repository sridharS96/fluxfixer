
WITH dim_sales_order_line_indicator__generate AS (
    SELECT
        'Undersupply Backordered' AS is_undersupply_backordered

    UNION ALL
    SELECT
        'Not Undersupply Backordered' AS is_undersupply_backordered

    UNION ALL
    SELECT
        'Undefined' AS is_undersupply_backordered

    UNION ALL
    SELECT
        'Invalid' AS is_undersupply_backordered
)

SELECT
    dim_sales_order_line_indicator.is_undersupply_backordered,
    dim_package_type.package_type_key,
    dim_package_type.package_type_name,
    FARM_FINGERPRINT(
        CONCAT(
            COALESCE(dim_sales_order_line_indicator.is_undersupply_backordered, 'Invalid'),
            ',',
            COALESCE(CAST(dim_package_type.package_type_key AS STRING), '-1')
        )
    ) AS sales_order_line_indicator_key
FROM
    dim_sales_order_line_indicator__generate AS dim_sales_order_line_indicator
CROSS JOIN
    {{ ref('dim_package_type') }} AS dim_package_type;
