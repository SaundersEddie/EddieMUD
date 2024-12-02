# EddieMUD

Python MUD Concept  
Nothing remarkable here, this is just for concepting ideas, and testing technologies while I mess with them.  
No timeline on completion, although I will likely do a very loose roadmap on features I'd like to implement.

Setup:

```
python -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt

For local testing:
pip install -r test-requirements.txt
```

Run:

```
PYTHONPATH=./src/python python -m EddieMUD.core.main
```

Testing:
Basic unit testing will be created by Eddie, however feel free to install pytest and  
create some tests.

Current Pytest version in use 8.3.3

https://docs.pytest.org/en/stable/getting-started.html#getstarted
