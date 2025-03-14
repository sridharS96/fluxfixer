
WITH dim_customer__source AS (
    SELECT
        *
    FROM `vit-lam-data.wide_world_importers.sales__customers`
)

, dim_customer__rename_recast AS (
    SELECT
        CAST(customer_id AS INT) AS customer_id
        , CAST(customer_name AS STRING) AS customer_name
        , CAST(is_statement_sent AS BOOLEAN) AS is_statement_sent_boolean
        , CAST(is_on_credit_hold AS BOOLEAN) AS is_on_credit_hold_boolean
        , CAST(payment_days AS INT) AS payment_days
        , CAST(credit_limit AS NUMERIC) AS credit_limit
        , CAST(standard_discount_percentage AS NUMERIC) AS standard_discount_percentage
        , CAST(bill_to_customer_id AS INT) AS bill_to_customer_key
        , CAST(customer_category_id AS INT) AS customer_category_key
        , CAST(buying_group_id AS INT) AS buying_group_key
        , CAST(primary_contact_person_id AS INT) AS primary_contact_person_key
        , CAST(alternate_contact_person_id AS INT) AS alternate_contact_person_key
        , CAST(delivery_method_id AS INT) AS delivery_method_key
        , CAST(delivery_city_id AS INT) AS delivery_city_key
        , CAST(account_opened_date AS DATE) AS account_opened_date
    FROM dim_customer__source
)

, dim_customer__convert_boolean AS (
    SELECT
        *
        , CASE
            WHEN is_statement_sent_boolean IS TRUE THEN 'Sent Statement'
            WHEN is_statement_sent_boolean IS FALSE THEN 'Not Sent Statement'
            WHEN is_statement_sent_boolean IS NULL THEN 'Undefined'
            ELSE 'Invalid' END
        AS is_statement_sent
        , CASE
            WHEN is_on_credit_hold_boolean IS TRUE THEN 'On Credit Hold'
            WHEN is_on_credit_hold_boolean IS FALSE THEN 'Not On Credit Hold'
            WHEN is_on_credit_hold_boolean IS NULL THEN 'Undefined'
            ELSE 'Invalid' END
        AS is_on_credit_hold
    FROM dim_customer__rename_recast
)

, dim_customer__handle_null AS (
    SELECT
        customer_id
        , customer_name
        , is_statement_sent
        , is_on_credit_hold
        , payment_days
        , credit_limit
        , standard_discount_percentage
        , COALESCE(bill_to_customer_key, 0) AS bill_to_customer_key
        , COALESCE(customer_category_key, 0) AS customer_category_key
        , COALESCE(buying_group_key, 0) AS buying_group_key
        , COALESCE(primary_contact_person_key, 0) AS primary_contact_person_key
        , COALESCE(alternate_contact_person_key, 0) AS alternate_contact_person_key
        , COALESCE(delivery_method_key, 0) AS delivery_method_key
        , COALESCE(delivery_city_key, 0) AS delivery_city_key
        , account_opened_date
    FROM dim_customer__convert_boolean
)

, dim_customer__add_undefined AS (
    SELECT
        customer_id
        , customer_name
        , is_statement_sent
        , is_on_credit_hold
        , payment_days
        , credit_limit
        , standard_discount_percentage
        , bill_to_customer_key
        , customer_category_key
        , buying_group_key
        , primary_contact_person_key
        , alternate_contact_person_key
        , delivery_method_key
        , delivery_city_key
        , account_opened_date
    FROM dim_customer__handle_null

    UNION ALL
    SELECT
        0 AS customer_id
        , 'Undefined' AS customer_name
        , 'Undefined' AS is_statement_sent
        , 'Undefined' AS is_on_credit_hold
        , NULL AS payment_days
        , NULL AS credit_limit
        , NULL AS standard_discount_percentage
        , 0 AS bill_to_customer_key
        , 0 AS customer_category_key
        , 0 AS buying_group_key
        , 0 AS primary_contact_person_key
        , 0 AS alternate_contact_person_key
        , 0 AS delivery_method_key
        , 0 AS delivery_city_key
        , NULL AS account_opened_date

    UNION ALL
    SELECT
        -1 AS customer_id
        , 'Invalid' AS customer_name
        , 'Invalid' AS is_statement
        , 'Invalid' AS is_on_credit
        , NULL AS payment_days
        , NULL AS credit_limit
        , NULL AS standard_discount_p
        , -1 AS bill_to_customer_key
        , -1 AS customer_category_key
        , -1 AS buying_group_key
        , -1 AS primary_contact_person
        , -1 AS alternate_contact_pers
        , -1 AS delivery_method_key
        , -1 AS delivery_city_key
        , NULL AS account_opened_date
)

SELECT
    CASE
        WHEN dim_customer.customer_id = 0 THEN 0
        WHEN dim_customer.customer_id = -1 THEN -1
        ELSE FARM_FINGERPRINT(
            dim_customer.customer_id || dim_membership.membership || dim_membership.begin_effective_date
        )
    END AS customer_key
    , dim_customer.customer_id
    , dim_customer.customer_name
    , dim_customer.is_statement_sent
    , dim_customer.is_on_credit_hold
    , dim_customer.payment_days
    , dim_customer.credit_limit
    , dim_customer.standard_discount_percentage
    , dim_membership.membership
    , dim_membership.begin_effective_date
    , dim_membership.end_effective_date
    , dim_customer.bill_to_customer_key
    , COALESCE(dim_customer_bill_to.customer_name, 'Invalid') AS bill_to_customer_name
    , dim_customer.customer_category_key
    , COALESCE(dim_customer_category.customer_category_name, 'Invalid') AS customer_category_name
    , dim_customer.buying_group_key
    , COALESCE(dim_buying_group.buying_group_name, 'Invalid') AS buying_group_name
    , dim_customer.primary_contact_person_key
    , COALESCE(dim_person_primary.full_name, 'Invalid') AS primary_contact_full_name
    , dim_customer.alternate_contact_person_key
    , COALESCE(dim_person_alternate.full_name, 'Invalid') AS alternate_contact_full_name
    , dim_customer.delivery_method_key
    , COALESCE(dim_delivery_method.delivery_method_name, 'Invalid') AS delivery_method_name
    , dim_customer.delivery_city_key
    , COALESCE(dim_city_delivery.city_name, 'Invalid') AS delivery_city_name
    , COALESCE(dim_city_delivery.state_province_key, -1) AS delivery_state_province_key
    , COALESCE(dim_city_delivery.state_province_name, 'Invalid') AS delivery_state_province_name
    , COALESCE(dim_city_delivery.sales_territory, 'Invalid') AS delivery_sales_territory
    , COALESCE(dim_city_delivery.country_key, -1) AS delivery_country_key
    , COALESCE(dim_city_delivery.country_name, 'Invalid') AS delivery_country_name
    , COALESCE(dim_city_delivery.country_type, 'Invalid') AS delivery_country_type
    , COALESCE(dim_city_delivery.continent_name, 'Invalid') AS delivery_continent_name
    , COALESCE(dim_city_delivery.region_name, 'Invalid') AS delivery_region_name
    , COALESCE(dim_city_delivery.subregion_name, 'Invalid') AS delivery_subregion_name
    , dim_customer.account_opened_date
FROM dim_customer__add_undefined AS dim_customer

LEFT JOIN dim_customer__add_undefined AS dim_customer_bill_to
    ON dim_customer.bill_to_customer_key = dim_customer_bill_to.customer_id

LEFT JOIN {{ ref('stg_dim_customer_category') }} AS dim_customer_category
    ON dim_customer.customer_category_key = dim_customer_category.customer_category_key

LEFT JOIN {{ ref('stg_dim_buying_group') }} AS dim_buying_group
    ON dim_customer.buying_group_key = dim_buying_group.buying_group_key

LEFT JOIN {{ ref('dim_person') }} AS dim_person_primary
    ON dim_customer.primary_contact_person_key = dim_person_primary.person_key

LEFT JOIN {{ ref('dim_person') }} AS dim_person_alternate
    ON dim_customer.alternate_contact_person_key = dim_person_alternate.person_key

LEFT JOIN {{ ref('dim_delivery_method') }} AS dim_delivery_method
    ON dim_customer.delivery_method_key = dim_delivery_method.delivery_method_key

LEFT JOIN {{ ref('dim_city') }} AS dim_city_delivery
    ON dim_customer.delivery_city_key = dim_city_delivery.city_key

LEFT JOIN {{ ref('dim_customer_membership') }} AS dim_membership
    ON dim_customer.customer_id = dim_membership.customer_id
;
