#!/usr/bin/env bash

# Data seed script for citrineos-core, run if prior to running the tests.
# https://citrineos.github.io/docs/getting-started.html
# Directus http://localhost:8055 admin@citrineos.com / CitrineOS!
# citrineos-core/Server/src/config/envs/local.ts or docker.ts configure how citrineos will enforce authentication

curl --location --request POST 'localhost:8080/data/configuration/password?callbackUrl=csms.pro/api/notifications' \
--header 'Content-Type: application/json' \
--data '{
  "stationId": "CP_1",
  "password": "0123456789123456",
  "setOnCharger": true
}'


