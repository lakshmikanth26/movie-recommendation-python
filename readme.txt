get api from this add in routes
https://www.themoviedb.org/settings/api

python version : Python 3.12.7
pip version : pip 23.3.2 

open terminal execute below commands

step 1 :  command
python -m venv venv

step 2 : command
.\venv\Scripts\activate

if error check it is restricted
 command :   Get-ExecutionPolicy
 if restricted
 command : Set-ExecutionPolicy RemoteSigned

step 3 : command
pip install -r requirements.txt

step 4 : command
python run.py
