# Library services

## Getting Started:
First you need to create a virtual environment to run the application, then install the dependencies. 

Run these commands inside the directory:
### For Linux:
```
python3 -m venv flaskApp
source flaskApp/bin/activate
pip3 install --upgrade pip
pip install -r requirements.txt
```

### For Windows:
```
py -3 -m venv flaskApp
flaskApp\Scripts\activate
pip3 install --upgrade pip
pip install -r requirements.txt
```

Once you have installed all the requirements stated above, you can run the Flask application with the following command:
```
python -m flask run
```


### Debugging: Flask Displaying Old Version

1. Display list of running Python processes...

```
$ ps -ef | grep python
```

Second column will contain the pid (process id).

Example Results:

```
user     727   689  0 01:27 pts/1    00:00:00 python3 -m flask run   <--- *culprit*
user    3861  2236  0 06:41 pts/0    00:00:00 grep python
```

2. Kill flask process using the pid...

```
$ kill -9 [pid]
```

Example:

```
$ kill -9 727
```

NOTE: If the issue is with regards to CSS changes only, use Ctrl + Shift + R in browser (works in both Chrome and Firefox).