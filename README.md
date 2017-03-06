# Aqara Gateway Python Library

[![Build Status](https://travis-ci.org/javefang/pyaqara.svg?branch=master)](https://travis-ci.org/javefang/pyaqara)

Python binding for the Aqara devices, based on protocol defined [here](https://github.com/louisZL/lumi-gateway-local-api)

The aim of this project is to abstract the protocol implementation details away and let
developer focus on developing features and integrations on top of the Aqara hardware, with
a focus on [HomeAssistant](https://github.com/home-assistant/home-assistant) integration.
It also protect developers from breaking changes in the API.

## Features

Supported Features
- Gateway discovery
- Sensor discovery
- Listen on sensor update
- Read sensor state

Supported Hardwares
  + Temperature and Humidity Sensor
  + Contact Sensor
  + Motion Sensor
  + Aqara Switch Sensor
  + Gateway LED (brightness and color)
