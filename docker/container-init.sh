#!/bin/bash -l
set -e
# Resolve our magic names to docker internal ip
awk '!/.*localmaeher.*/' /etc/hosts >/etc/hosts.new && cat /etc/hosts.new >/etc/hosts
echo "$(getent ahostsv4 host.docker.internal | awk '{ print $1 }') localmaeher.dev.pvarki.fi mtls.localmaeher.dev.pvarki.fi tak.localmaeher.dev.pvarki.fi  mtx.localmaeher.dev.pvarki.fi" >>/etc/hosts
cat /etc/hosts
if [ -f /data/persistent/firstrun.done ]
then
  echo "First run already cone"
else
  if [ -f /pvarki/kraftwerk-init.json ]
  then
    # Do the normal init
    /kw_product_init init /pvarki/kraftwerk-init.json
    date -u +"%Y%m%dT%H%M" >/data/persistent/firstrun.done
  else
    echo "Kraftwerk manifest not present"
  fi
fi
