
# OCTT Implementation

Python (pytest) implementation of the OCTT tests, currently focusing on the CSMS tests.

This is a work in progress with the aim of implementing the entire test suite.

Implemented tests

* TC_A_01_CSMS
* TC_A_02_CSMS
* TC_A_03_CSMS

[csms.py](/csms.py) - Mock in memory CSMS which you can test against - Can be used to checkout the tests, definitely not a complete implementation of a CSMS.


### Install depenandices
```
pip install -r requirements.txt
```

### Run tests
```
pytest -v -p no:warnings test_tc_a_01_02_03_csms.py
```

## Configuration / Environment Variables

To run this project, you will need to set the following environment variables through [pytest.ini](/pytest.ini) or manually.

`CSMS_ADDRESS`

`TEST_USER_NAME`

`TEST_USER_PASSWORD`

## Contributing

Contributions are welcome through PRs!

Please adhere to this project's `code of conduct`.


## Authors

[tzi.app](https://www.tzi.app)


## License

[MIT](https://choosealicense.com/licenses/mit/)

