#!/usr/bin/env ruby

#mac_sip_status.rb
require 'facter'
Facter.add(:mac_sip_status) do
  confine :kernel => "Darwin"
  setcode do
    osver = Facter.value('macosx_productversion_major')
    if osver == "10.11"
      output = Facter::Util::Resolution.exec("/usr/bin/csrutil status")
      enabled = output.split("\n").first
      if enabled=="System Integrity Protection status: enabled."
        "enabled"
      else
        "disabled"
      end
    else
      "Not supported on this OS version"
    end
  end
end
