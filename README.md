# database-operator
Basic database operator application commonly built in Model-View-Controller (MVC) architecture.  
Takes an example database and extracts its table names, column names & types, and foreign keys of the tables. (which tables are related to each other)

## Infrastructure
* Python 3.5.2 for the backend implementation.
* Qt 5.15.2 and QML for the User-Interface (UI) implementation.
* PyQt5 for Python and Qt entegration.
* SQLite 3.11.0 for database operations.

## Prerequisites
```
$ pip install PySide2
```

## Visuals
The example database that is imported to application: (Reference: [link to chinook SQLite sample database!](https://www.sqlitetutorial.net/sqlite-sample-database/))  
![Image of chinook SQLite sample database](https://github.com/akngmskvk/database-operator/blob/main/images/chinook-diagram.png)  


Screenshots of the login screen:  
![login-1](https://github.com/akngmskvk/database-operator/blob/main/images/img0.png) ![login-2](https://github.com/akngmskvk/database-operator/blob/main/images/img1.png)  


Screenshots of after database is extracted:  
![main-1](https://github.com/akngmskvk/database-operator/blob/main/images/img2.png) ![main-2](https://github.com/akngmskvk/database-operator/blob/main/images/img3.png)  



