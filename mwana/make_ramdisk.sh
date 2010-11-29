#!/bin/sh

usage()
{
cat <<EOF
This is helpful for speeding up tests. Have test_localsettings.py
  point to /tmp/ramdisk/test_db.sqlite3 after mounting a ramdisk
  with this script.
usage: $0 [-m] [-l] [-s]
OPTIONS:
   -m      Make Mac OS X Ramdisk
   -l      Make Linux ramdisk (Ubuntu, not yet implemented)
   -s      Make Suse ramdisk 
EOF
}

make_mac_ramdisk() {
  # See: http://reviews.cnet.com/8301-13727_7-20020071-263.html
  NUMSECTORS=16000 # ~8 meg
  ramdisk=`hdid -nomount ram://$NUMSECTORS`
  newfs_hfs $ramdisk
  mkdir /tmp/ramdisk
  mount -t hfs $ramdisk /tmp/ramdisk
}

make_linux_ramdisk() {
  echo 'TODO - I did not test it on linux'
  # See: http://www.linuxscrew.com/2010/03/24/fastest-way-to-create-ramdisk-in-ubuntulinux/
  # sudo mkdir /tmp/ramdisk
  # sudo chmod 777 /tmp/ramdisk
  # sudo mount -t tmpfs -o size=8M tmpfs /tmp/ramdisk/
}

make_suse_ramdisk() {
  sudo mknod /dev/ram1 b 1 1
  sudo chown root:disk /dev/ram1 
  sudo chmod 0660 /dev/ram1 
  sudo mkfs -t ext4 -q /dev/ram1 131072
  sudo mkdir -p /tmp/ramcache
  sudo mount /dev/ram1 /tmp/ramdisk
  sudo chmod 777 /tmp/ramdisk
}

while getopts "mlsh" OPTION
do
    case $OPTION in
        m)
            make_mac_ramdisk
            exit 0
            ;;
        l)
            make_linux_ramdisk
              echo "TODO: implement me (see this script for possible example)"
            exit 1 # TODO exit 1 when implemented
            ;;
        s)
            make_suse_ramdisk
            exit 0
            ;;
        ?)
            usage
            exit
            ;;
    esac
done
usage
