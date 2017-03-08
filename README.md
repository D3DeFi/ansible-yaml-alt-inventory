Description
-----------

This project presents alternative way to define hosts in Ansible inventory. By default, you are assigning host to groups resulting in multiple occurences of that host. This can get messy if you are using a lot of groups and trying to keep up a record of which host has which groups.

Would you rather have a single definition of host and a list of groups assigned to it, maybe this dynamic inventory is for you.

Installation & Usage
--------------------
* Clone this project to your ansible controller host
* Install required Python packages
```
pip install -r requirements.txt
```
* Copy file **yaml-inventory-loader.py** into folder named **inventory** inside your Ansible project
* Add following directive into ansible.cfg located inside your Ansible project (see examples/ in this repo):
```
[defaults]
inventory = inventory
```
* Create YAML files inside inventory/ folder in your Ansible project (see examples/ in this repo). E.g. prod.yml:
```
dev01.example.com:
  groups: UK, proxy, apache-php
  ansible_port: 8998

dev[02:04].example.com:
  groups: UK, proxy, mysql
  ansible_port: 8999
  mylist:
    - item1
    - item2
```
