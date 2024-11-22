#!/usr/bin/env bash

# Data seed script for MaEVe, run if prior to running the tests.

curl http://localhost:9410/api/v0/cs/CP_1 -H 'content-type: application/json' -d '{"securityProfile": 0,"base64SHA256Password": "XohImNooBHFR0OVvjcYpJ3NgPQ1qq73WKhHvch0VQtg=", "invalidUsernameAllowed": false}'
