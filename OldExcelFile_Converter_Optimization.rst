Optimization of Converter for old Excel files
=============================================

This file documents the modification of savetojson.py to allow usage of old Excel files.
This mostly consists of checking the file for problematic content and issuing a fitting warning.
Warnings inform the user and provide a guideline on how to make the file compliant to needed standards.

Reasoning
---------
The GUI uses json files to save and load configurations of urbs but especially older configurations only exist in excel files.

Therefore some form of compatibility with these older files was 