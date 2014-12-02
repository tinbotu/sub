# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "sub_ubuntu_14.04"
  config.vm.box_url = "https://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"

  config.vm.hostname = 'subculture.local'
  #config.vm.network :forwarded_port, guest: 8900, host: 8900
  #config.vm.network :private_network, ip: "192.168.50.14"

  #config.vm.provider :virtualbox do |vb|
  #  vb.customize ["modifyvm", :id, "--memory", "6144", "--cpus", "5", "--ioapic", "on"]
  #end
  config.vm.provision :shell, :privileged => false, :path => 'script/devserver_provisioning.sh'
end
