#chasetb-mac_facts

Custom Facts written for OS X machines. Fact files were intended to be used with Sal or standalone Facter installs.

======

##Installation Package

Run the installation package to have these Facts automatically installed on your machine or deployed to a remote machine. Installation package assumes Facts will be used with Sal.

======

##Manual Installation

For use with Sal, place facts files ending in `.rb` in `/usr/local/sal/facter/`

For standalone Facter use, place facts files ending in `.rb` in `/usr/lib/ruby/site_ruby/facter`

Place external Facts in `/etc/facter/facts.d/` (You may need to create this directory)

##Fact Descriptions

###mac_sip_enabled

Displays current status of System Integrity Protection

###mac_warranty

External fact that reports two facts: AppleCare machine name and machine warranty expiration