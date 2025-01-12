CREATE TABLE Customer (
    CustomerGUID UUID PRIMARY KEY,
    CustomerID INT,
    FullName VARCHAR(255),
    Segment VARCHAR(255)
);

CREATE TABLE Product (
    ProductGUID UUID PRIMARY KEY,
    ProductID INT,
    Category VARCHAR(255),
    SubCategory VARCHAR(255),
    Container VARCHAR(255)
);

CREATE TABLE "Order" (
    OrderGUID UUID PRIMARY KEY,
    OrderID INT,
    DateOrdered TIMESTAMP,
    Priority VARCHAR(255),
    CustomerGUID UUID REFERENCES Customer(CustomerGUID),
    ShippingGUID UUID REFERENCES Shipping(ShippingGUID),
    ProductGUID UUID REFERENCES Product(ProductGUID)
);

CREATE TABLE Shipping (
    ShippingGUID UUID PRIMARY KEY,
    ShippingID INT,
    DateShipped TIMESTAMP,
    ShippingCost MONEY,
    ShipMode VARCHAR(255),
    AddressGUID UUID REFERENCES Address(AddressGUID)
);

CREATE TABLE Address (
    AddressGUID UUID PRIMARY KEY,
	AddressID INT,
    Region VARCHAR(255),
    State_Province VARCHAR(255),
    City VARCHAR(255),
    PostalCode VARCHAR(255),
    CustomerGUID UUID REFERENCES Customer(CustomerGUID)
);

CREATE TABLE Sales (
    SalesGUID UUID PRIMARY KEY,
    SalesID INT,
    Profit MONEY,
    Sales MONEY,
    QuantityOrdered INT,
    ProductBaseMargin MONEY,
    Discount DECIMAL,
    UnitPrice MONEY,
    OrderGUID UUID REFERENCES "Order"(OrderGUID),
    ProductGUID UUID REFERENCES Product(ProductGUID)
);




