-- Sample SQL code with intentional mistakes

-- Mistake 1: Incorrect table name (should be "Customers", not "Custmers")
SELECT *
FROM Custmers
WHERE City = 'London';

-- Mistake 2: Missing quotation marks around a string literal (should be 'New York')
SELECT *
FROM Orders
WHERE CustomerName = New York;

-- Mistake 3: Using a reserved keyword as a column name (should be something like "OrderDate", not "Date")
SELECT Date, ProductID
FROM Orders
GROUP BY Orders;

-- Mistake 4: Incorrect syntax for a WHERE clause (should be "WHERE Price > 50", not "WHERE Price MORE THAN 50")
SELECT ProductName
FROM Products
WHERE Price MORE THAN 50;

--Mistake 5: Incorrect aggregation function. There is no AVG_PRICE function.
SELECT customerId, AVG_PRICE(orderTotal)
FROM Orders
GROUP BY customerId;

--Mistake 6: Missing comma in column list.
SELECT firstName lastName
FROM Employees;

--Mistake 7: Attempting to use a column alias in the WHERE clause (aliases cannot be used in WHERE clauses, they are applied after. The where clause must use the actual column name)
SELECT price AS productPrice
FROM Products
WHERE productPrice > 100;

--Mistake 8: Attempting to update a column that does not exist.
UPDATE Products
SET color = 'Red'
WHERE productID = 1;

--Mistake 9: Using the wrong comparison operator for a NULL check (should be "IS NULL", not "= NULL")
SELECT * FROM Employees WHERE department = NULL;

--Mistake 10: Incorrect join syntax. It is missing the ON clause.
SELECT Customers.customerName, Orders.orderID
FROM Customers
JOIN Orders;
