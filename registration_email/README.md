# registration_email_performance_timer

A simple utility container to time how long it takes to receive the registration verification email when a user registers.
Results are output in the influxdb line protocol, and can be directly ingested into influxdb.

### Usage:

```
export GALAXY_SERVER=https://dev.usegalaxy.org.au
export GALAXY_EMAIL="user@gmail.com"
export GALAXY_USERNAME="user"
export GALAXY_PASSWORD="pass"
export IMAP_SERVER=imap.gmail.com
export IMAP_USERNAME=usegalaxyaustresstest@gmail.com
export IMAP_PORT=993
docker run -e GALAXY_SERVER -e GALAXY_USERNAME -e GALAXY_PASSWORD -e GALAXY_EMAIL -e IMAP_SERVER -e IMAP_USERNAME -e IMAP_PORT -it usegalaxyau/registration_email_perf_timer:latest
```

### Output:

```
email_verification,server=https://dev.usegalaxy.org.au,email=usegalaxyaustresstest+test10@gmail.com,status=success result=1.654414176940918 1680356313583343000
```

### Help
```
usage: registration_email_perf_timer.py [-h] [-s SERVER] [-e EMAIL] [-u USERNAME] [-p PASSWORD] [-i IMAP_SERVER] [-o IMAP_PORT] [-m IMAP_USERNAME] [-a IMAP_PASSWORD]

Register a user, and check whether a registration email is received.

options:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        Galaxy server url
  -e EMAIL, --email EMAIL
                        Email address to use when registering the user (or set GALAXY_EMAIL env var)
  -u USERNAME, --username USERNAME
                        Username to use when registering the user (or set GALAXY_USERNAME env var)
  -p PASSWORD, --password PASSWORD
                        Password to use when registering the user (or set GALAXY_PASSWORD env var)
  -i IMAP_SERVER, --imap_server IMAP_SERVER
                        IMAP server to use when checking for receipt of email (or set IMAP_SERVER env var)
  -o IMAP_PORT, --imap_port IMAP_PORT
                        IMAP port to use when checking for receipt of email (or set IMAP_PORT env var)
  -m IMAP_USERNAME, --imap_username IMAP_USERNAME
                        IMAP username to use when checking for receipt of email (or set IMAP_USERNAME env var)
  -a IMAP_PASSWORD, --imap_password IMAP_PASSWORD
                        IMAP password to use when checking for receipt of email (or set IMAP_PASSWORD env var)
```
