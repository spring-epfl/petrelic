# -*- mode: ruby -*-
# vi: set ft=ruby :

$change_vsyscall = <<-EOF
echo 'Enable vsyscall emulation.'
sed 's/GRUB_CMDLINE_LINUX_DEFAULT="\(.\+\)"/GRUB_CMDLINE_LINUX_DEFAULT="\1 vsyscall=emulate"/g' /etc/default/grub
update-grub
EOF

Vagrant.configure("2") do |config|
  config.vm.box = "generic/debian10"
  config.vm.synced_folder ".", "/host"
  config.vm.provision :docker
  config.vm.provision "shell", inline: $change_vsyscall
  config.vm.provision :reload
end
