# Database-for-Order-Management-in-E-commerce-Platform
Description:
The Administrator of order management system could monitor, create, even delete many information of orders 
in this system which is for a E-commercial company. He can obtain details of orders in order table and find which 
employee has operated this order in order_manage table. When he enters employee table, he could get infomation 
of employees in this company and which department they work in. After that, products ought to be controlled by 
employees and deals should be created by departments. From another side, Administrator could see the progress 
that customers will purchase some products directly or add products to their carts. Therefore, orders might be 
created from products or from carts.

Employee page contains data that are extracted from 'employee join department', so Administrator could know 
concrete names of departments which employees work in and ensure employees work in a correct department which
is in a same timezone.

We use SQL--"GROUP BY p_id" in product page, in order to show this page sorting by the porduct. As we all know, 
in different view time, information of same product changes a lot, like price, status... So every row of product table
shows various details, and that is why we want to sort the table by product id.

We created the user interface on the pages "order, employee, and select." Take an example using the "order" part, 
which is functioned by "adding", "delete", and "changing" data. Based on the elements from the "order": order_id, 
total_price, created_date, order_city, order_country, order_zipcode. The data can be added and deleted by directly 
clicking the buttons "add" or "delete". Also, once the update button has been clicked, the data can be directly changed 
because all the data will be auto-filled up in the same place that was used for adding data. The "add" button will be changed 
to the "update" button, which is allowed to click for finishing the data change. I believe it is a funny function 
because it does interact with the users in a funny way. The function of "adding, deleting, and changing" data 
is also very useful that convenient for the users to manage the data. 
