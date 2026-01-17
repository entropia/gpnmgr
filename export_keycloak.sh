#!/bin/bash

sudo docker exec -it gpnmgr-keycloak-1 sh -c "/opt/keycloak/bin/kc.sh export --realm gpnmgr --users realm_file --file /tmp/export.json"
sudo docker cp gpnmgr-keycloak-1:/tmp/export.json ./gpnmgr-realm.json
