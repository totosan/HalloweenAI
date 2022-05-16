#!/bin/bash
gunicorn --bind 0.0.0.0:3500 wsgi:app