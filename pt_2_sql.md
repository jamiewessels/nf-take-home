#### Question 1

WITH users_grouped AS 
    (SELECT 
        user_id, DATE_PART('year', created_at) as year,
        DATE_PART('month', created_at) as month 
    FROM users), 

    ex_grouped AS
        (SELECT 
            user_id, 
            DATE_PART('year', exercise_completion_date) as year,
            DATE_PART('month', exercise_completion_date) as month 
        FROM exercises), 

    combined AS
        (SELECT 
            u.year, 
            u.month, 
            u.user_id, 
            e.user_id AS first_month
        FROM users_grouped u
        LEFT JOIN ex_grouped e
        ON u.user_id = e.user_id AND u.year = e.year AND u.month = e.month)

SELECT 
    c.year, 
    c.month, 
    CAST (SUM(CASE WHEN first_month > 0 THEN 1 ELSE 0 END) AS REAL) / COUNT(1) AS percent_first_month
FROM combined c
GROUP BY c.year, c.month;


#### Question 2

WITH user_counts AS
    (SELECT 
        user_id, 
        COUNT(1) as activity_counts 
    FROM exercises
    GROUP BY user_id)

SELECT 
    activity_counts, 
    COUNT(1) as num_users 
FROM user_counts
GROUP BY activity_counts
ORDER BY activity_counts;

#### Question 3

SELECT 
    pr.organization_name, 
    AVG(ph.score) AS org_avg 
FROM providers pr
JOIN Phq9 ph
ON pr.provider_id = ph.provider_id
GROUP BY pr.organization_id, pr.organization_name
ORDER BY org_avg DESC  
LIMIT 5;